# coding=utf-8
"""
    Copyright (c) 2018-present, Ant Financial Service Group

    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

        http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.
   ------------------------------------------------------
   File Name : aio_listener
   Author : jiaqi.hjq
"""
# Needs python >= 3.4
import asyncio
import logging
import threading
import traceback
import opentracing

try:
    import uvloop

    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
except ImportError:
    pass

from threading import RLock
from mytracer.helpers import tracer
from concurrent.futures import ThreadPoolExecutor

from anthunder.command.fail_response import FailResponse
from anthunder.command.heartbeat import HeartbeatResponse
from anthunder.exceptions import ServerError, ClientError
from anthunder.protocol import BoltRequest, SofaHeader, BoltResponse
from anthunder.protocol.constants import PTYPE, CMDCODE, RESPSTATUS
from anthunder.protocol.exceptions import ProtocolError
from .base_listener import BaseListener, BaseHandler

logger = logging.getLogger(__name__)


class NoProcessorError(ServerError):
    pass


class AioThreadpoolRequestHandler(BaseHandler):
    MAX_WORKER = 30

    def __init__(self):
        self.executor = ThreadPoolExecutor(max_workers=self.MAX_WORKER)
        self.local = threading.local()
        self.lock = RLock()

    def handle_request(self, spanctx, service, method, body):
        """do not run heavy job here, just put payloads to executors and return future object"""
        try:
            ServiceCls = self.interface_mapping[service]
        except KeyError as e:
            logger.error("Service not found in interface registry: [{}]".format(service))
            raise NoProcessorError("Service not found in interface registry: [{}]".format(service)) from e
        try:
            svc_obj = ServiceCls(spanctx)
            func = getattr(svc_obj, method)
        except AttributeError as e:
            logger.error("No such method[{}]".format(method))
            raise NoProcessorError("No such method[{}]".format(method)) from e

        future = self.executor.submit(func, body)
        return future

    def register_interface(self, interface, service_cls):
        """
        register interface: service_cls relationship
        :param interface:
        :param service_cls:
        :return:
        """
        with self.lock:
            self.interface_mapping[interface] = service_cls


class AioListener(BaseListener):
    handlerCls = AioThreadpoolRequestHandler

    def __init__(self, *args, **kwargs):
        super(AioListener, self).__init__(*args, **kwargs)
        self._loop = asyncio.new_event_loop()
        self._server = None

    def initialize(self):
        pass

    def run_forever(self):
        """loop thread"""
        # asyncio.set_event_loop(self._loop)
        coro = asyncio.start_server(self._handler_connection, *self.address, loop=self._loop, **self.server_kwargs)
        self._server = self._loop.run_until_complete(coro)
        self._loop.run_forever()

    def shutdown(self):
        """quit the server loop"""
        if self._loop and self._server:
            self._server.close()
            asyncio.run_coroutine_threadsafe(self._server.wait_closed(), self._loop)

    @asyncio.coroutine
    def _dispatch(self, call_type, request_id, sofa_header, body, *, timeout_ms, writer):
        """send request to handler"""
        service = sofa_header.get('sofa_head_target_service') or sofa_header.get('service')
        if not service:
            yield from self._write_msg(writer,
                                       FailResponse.response_to(request_id, RESPSTATUS.CLIENT_SEND_ERROR).to_stream())
            logger.error("Missing service name in sofa header [{}]".format(sofa_header))
            return
        method = sofa_header.get('sofa_head_method_name')
        if not method:
            yield from self._write_msg(writer,
                                       FailResponse.response_to(request_id, RESPSTATUS.CLIENT_SEND_ERROR).to_stream())
            logger.error("Missing method name in sofa header [{}]".format(sofa_header))
            return

        spanctx = tracer.extract(opentracing.Format.TEXT_MAP, sofa_header)

        try:
            future = self.handler.handle_request(spanctx, service, method, body)
        except NoProcessorError:
            yield from self._write_msg(writer,
                                       FailResponse.response_to(request_id, RESPSTATUS.NO_PROCESSOR).to_stream())
            return
        except Exception:
            yield from self._write_msg(writer,
                                       FailResponse.response_to(request_id, RESPSTATUS.SERVER_EXCEPTION).to_stream())
            return
        if PTYPE.ONEWAY.value == call_type:
            # Just return future
            return future

        try:
            afut = asyncio.wrap_future(future)
            result = yield from asyncio.wait_for(afut, timeout_ms / 1000 if timeout_ms > 0 else None)
        except (asyncio.CancelledError, asyncio.TimeoutError) as e:
            logger.error("Task run cancelled/timeout in {}ms, service:[{}]: error:[{}]".format(timeout_ms, service, e))
            yield from self._write_msg(writer, FailResponse.response_to(request_id, RESPSTATUS.TIMEOUT).to_stream())
            return
        except Exception:
            logger.error(traceback.format_exc())
            yield from self._write_msg(writer, FailResponse.response_to(request_id, RESPSTATUS.UNKNOWN).to_stream())
            return

        if result:
            header = dict()
            tracer.inject(spanctx, opentracing.Format.TEXT_MAP, header)
            pkg = BoltResponse.response_to(result, request_id=request_id)
            try:
                yield from self._write_msg(writer, pkg.to_stream())
            except Exception:
                logger.error(traceback.format_exc())

    @asyncio.coroutine
    def _write_msg(self, writer, msg):
        yield from writer.drain()  # clean the buffer, avoid backpressure
        writer.write(msg)
        yield from writer.drain()

    @asyncio.coroutine
    def _handler_connection(self, reader, writer):
        """
        Full duplex model
        Only recv request here, run a new coro to process and send back response in same connection.
        """
        while True:
            try:
                fixed_header_bs = yield from reader.readexactly(BoltRequest.bolt_header_size())
                header = BoltRequest.bolt_header_from_stream(fixed_header_bs)
                call_type = header['ptype']
                cmdcode = header['cmdcode']

                class_name = yield from reader.readexactly(header['class_len'])

                bs = yield from reader.readexactly(header['header_len'])
                sofa_header = SofaHeader.from_bytes(bs)
                body = yield from reader.readexactly(header['content_len'])

                if cmdcode == CMDCODE.HEARTBEAT:
                    asyncio.ensure_future(
                        self._write_msg(writer, HeartbeatResponse.response_to(header['request_id']).to_stream()))
                    continue

                if cmdcode == CMDCODE.RESPONSE:
                    raise ClientError("wrong cmdcode:[{}]".format(cmdcode))

                if class_name != "com.alipay.sofa.rpc.core.request.SofaRequest".encode():
                    raise ClientError("wrong class_name:[{}]".format(class_name))

                asyncio.ensure_future(self._dispatch(call_type, header['request_id'], sofa_header, body,
                                                     timeout_ms=header['timeout'], writer=writer))
            except ClientError as e:
                logger.error(str(e))
                yield from self._write_msg(writer, FailResponse.response_to(header['request_id'],
                                                                            RESPSTATUS.CLIENT_SEND_ERROR).to_stream())
                continue

            except ProtocolError as e:
                logger.error(str(e))
                yield from self._write_msg(writer, FailResponse.response_to(header['request_id'],
                                                                            RESPSTATUS.CODEC_EXCEPTION).to_stream())
                continue

            except EOFError as e:
                logger.info("Connection closed: {}".format(e))
                try:
                    yield from writer.drain()  # clean the buffer, avoid backpressure
                    writer.write(FailResponse.response_to(header['request_id'],
                                                          RESPSTATUS.CONNECTION_CLOSED).to_stream())
                except:
                    pass
                writer.write_eof()
                yield from writer.drain()
                writer.close()
                break

            except Exception:
                logger.error(traceback.format_exc())
                try:
                    yield from writer.drain()  # clean the buffer, avoid backpressure
                    writer.write(FailResponse.response_to(header['request_id'], RESPSTATUS.UNKNOWN).to_stream())
                except:
                    pass
                writer.write_eof()
                yield from writer.drain()
                writer.close()
                break

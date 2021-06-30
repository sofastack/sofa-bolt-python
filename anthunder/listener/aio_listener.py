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

from anthunder.listener.base_listener import NoProcessorError

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
from anthunder.exceptions import ClientError
from anthunder.protocol import BoltRequest, SofaHeader, BoltResponse
from anthunder.protocol.constants import PTYPE, CMDCODE, RESPSTATUS
from anthunder.protocol.exceptions import ProtocolError
from .base_listener import BaseListener, BaseHandler

logger = logging.getLogger(__name__)


class AioThreadpoolRequestHandler(BaseHandler):
    MAX_WORKER = 30

    def __init__(self):
        self.executor = ThreadPoolExecutor(max_workers=self.MAX_WORKER)
        self.local = threading.local()
        self.lock = RLock()

    def handle_request(self, spanctx, service, method, body):
        """do not run heavy job here, just put payloads to executors and return future object"""
        logger.info("receive biz request of {}:{}".format(service, method))
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
        logger.info("biz request submitted to function({})".format(func))
        return future

    def register_interface(self, interface, service_cls, *service_cls_args, **service_cls_kwargs):
        """
        register interface: service_cls relationship
        :param interface: the interface name bind to the service
        :param service_cls: the service class factory. 
                            Will be called will a spanctx of each request and returns a Service Object.
        :param service_cls_args: extra positional arguments for service_cls
        :param service_cls_kwargs: extra keyword arguments for service_cls
        :return: None
        """
        with self.lock:
            if service_cls_args or service_cls_kwargs:
                def service_cls_wrapper(spanctx):
                    return service_cls(spanctx, *service_cls_args, **service_cls_kwargs)
            else:
                service_cls_wrapper = service_cls
            self.interface_mapping[interface] = service_cls_wrapper


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
        asyncio.set_event_loop(self._loop)
        coro = asyncio.start_server(self._handler_connection, *self.address, **self.server_kwargs)
        self._server = self._loop.run_until_complete(coro)
        logger.info("Aio Listener initialized, entering event loop")
        self._loop.run_forever()

    def shutdown(self):
        """quit the server loop"""
        logger.info("Aio Listener shutting down")
        if self._loop and self._server:
            self._server.close()
            asyncio.run_coroutine_threadsafe(self._server.wait_closed(), self._loop)

    async def _dispatch(self, call_type, request_id, sofa_header, body, *, timeout_ms, codec, writer):
        """send request to handler"""
        service = sofa_header.get('sofa_head_target_service') or sofa_header.get('service')
        if not service:
            await self._write_msg(
                writer,
                FailResponse.response_to(request_id,
                                         RESPSTATUS.CLIENT_SEND_ERROR,
                                         codec=codec).to_stream(),
            )
            logger.error("Missing service name in sofa header [{}]".format(sofa_header))
            return
        method = sofa_header.get('sofa_head_method_name')
        if not method:
            await self._write_msg(
                writer,
                FailResponse.response_to(request_id,
                                         RESPSTATUS.CLIENT_SEND_ERROR,
                                         codec=codec).to_stream())
            logger.error("Missing method name in sofa header [{}]".format(sofa_header))
            return

        spanctx = tracer.extract(opentracing.Format.TEXT_MAP, sofa_header)

        try:
            future = self.handler.handle_request(spanctx, service, method, body)
        except NoProcessorError:
            await self._write_msg(
                writer,
                FailResponse.response_to(request_id,
                                         RESPSTATUS.NO_PROCESSOR,
                                         codec=codec).to_stream(),
            )
            return
        except Exception:
            await self._write_msg(
                writer,
                FailResponse.response_to(request_id,
                                         RESPSTATUS.SERVER_EXCEPTION,
                                         codec=codec).to_stream(),
            )
            return
        if PTYPE.ONEWAY == call_type:
            # Just return future
            return future

        try:
            afut = asyncio.wrap_future(future)
            result = await asyncio.wait_for(afut, timeout_ms / 1000 if timeout_ms > 0 else None)
        except (asyncio.CancelledError, asyncio.TimeoutError) as e:
            logger.error("Task run cancelled/timeout in {}ms, service:[{}]: error:[{}]".format(timeout_ms, service, e))
            await self._write_msg(
                writer,
                FailResponse.response_to(request_id,
                                         RESPSTATUS.TIMEOUT,
                                         codec=codec).to_stream(),
            )
            return
        except Exception:
            logger.error(traceback.format_exc())
            await self._write_msg(
                writer,
                FailResponse.response_to(request_id,
                                         RESPSTATUS.UNKNOWN,
                                         codec=codec).to_stream(),
            )
            return

        if result:
            header = dict()
            tracer.inject(spanctx, opentracing.Format.TEXT_MAP, header)
            pkg = BoltResponse.response_to(result,
                                           request_id=request_id,
                                           codec=codec)
            try:
                await self._write_msg(writer, pkg.to_stream())
            except Exception:
                logger.error(traceback.format_exc())

    async def _write_msg(self, writer, msg):
        await writer.drain()  # clean the buffer, avoid backpressure
        writer.write(msg)
        await writer.drain()

    async def _handler_connection(self, reader, writer):
        """
        Full duplex model
        Only recv request here, run a new coro to process and send back response in same connection.
        """
        logger.info("connection created.")
        first_req = True
        while True:
            try:
                try:
                    fixed_header_bs = await reader.readexactly(BoltRequest.bolt_header_size())
                except asyncio.IncompleteReadError:
                    if first_req:
                        # just connected, do nothing. most likely L4 health checks from mosn/upstream
                        break
                    # break the loop
                    raise

                first_req = False
                logger.debug("received bolt header({})".format(fixed_header_bs))
                header = BoltRequest.bolt_header_from_stream(fixed_header_bs)
                call_type = header['ptype']
                cmdcode = header['cmdcode']

                class_name = await reader.readexactly(header['class_len'])
                logger.debug("received classname({})".format(class_name))

                bs = await reader.readexactly(header['header_len'])
                logger.debug("received sofa header({})".format(bs))

                sofa_header = SofaHeader.from_bytes(bs)
                body = await reader.readexactly(header['content_len'])
                logger.debug("received sofa body({})".format(body))

                if cmdcode == CMDCODE.HEARTBEAT:
                    logger.info("received heartbeat, request_id={}".format(header['request_id']))
                    asyncio.ensure_future(
                        self._write_msg(writer, HeartbeatResponse.response_to(header['request_id']).to_stream()))
                    continue

                if cmdcode == CMDCODE.RESPONSE:
                    raise ClientError("wrong cmdcode:[{}]".format(cmdcode))

                if class_name != "com.alipay.sofa.rpc.core.request.SofaRequest".encode():
                    raise ClientError("wrong class_name:[{}]".format(class_name))

                logger.debug("dispatching request[{}]".format(header['request_id']))
                asyncio.ensure_future(
                    self._dispatch(call_type,
                                   header['request_id'],
                                   sofa_header,
                                   body,
                                   timeout_ms=header['timeout'],
                                   codec=header['codec'],
                                   writer=writer))
            except ClientError as e:
                logger.error(str(e) + " returning CLIENT_SEND_ERROR")
                await self._write_msg(writer, FailResponse.response_to(header['request_id'],
                                                                       RESPSTATUS.CLIENT_SEND_ERROR).to_stream())
                continue

            except ProtocolError as e:
                logger.error(str(e) + " returning CODEC_EXCEPTION")
                await self._write_msg(writer, FailResponse.response_to(header['request_id'],
                                                                       RESPSTATUS.CODEC_EXCEPTION).to_stream())
                continue

            except EOFError as e:
                logger.warning("Connection closed by remote: {}".format(e))
                try:
                    await writer.drain()  # clean the buffer, avoid backpressure
                    writer.write(FailResponse.response_to(header['request_id'],
                                                          RESPSTATUS.CONNECTION_CLOSED).to_stream())
                except:
                    pass
                try:
                    writer.write_eof()
                    await writer.drain()
                except:
                    pass
                writer.close()
                break

            except Exception:
                logger.error("Unknow exception, close connection")
                logger.error(traceback.format_exc())
                try:
                    await writer.drain()  # clean the buffer, avoid backpressure
                    writer.write(FailResponse.response_to(header['request_id'], RESPSTATUS.UNKNOWN).to_stream())
                except:
                    pass
                try:
                    writer.write_eof()
                    await writer.drain()
                except:
                    pass
                writer.close()
                break

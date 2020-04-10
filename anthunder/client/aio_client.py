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
   File Name : aio_client
   Author : jiaqi.hjq
"""
# Needs python >= 3.4
import asyncio
import functools
import logging
import threading
import traceback
from contextlib import suppress

try:
    import uvloop

    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
except ImportError:
    pass
from concurrent.futures import TimeoutError, CancelledError

from anthunder.command.heartbeat import HeartbeatRequest
from anthunder.exceptions import PyboltError, ServerError
from anthunder.helpers.singleton import Singleton
from anthunder.protocol import SofaHeader, BoltRequest, BoltResponse
from anthunder.protocol.constants import PTYPE, CMDCODE, RESPSTATUS

from .base import _BaseClient

logger = logging.getLogger(__name__)


class AioClient(_BaseClient):
    __metaclass__ = Singleton
    """bolt client implemented with asyncio"""

    def __init__(self, app_name, **kwargs):
        super(AioClient, self).__init__(app_name, **kwargs)
        self._loop = asyncio.new_event_loop()
        self.request_mapping = dict()  # request_id: event
        self.response_mapping = dict()  # request_id: response_pkg
        self.connection_mapping = dict()  # address: (reader_coro, writer)
        self.loop_thread = self._init()
        self._pending_dial = dict()  # address: (asyncio.Lock)

    def _init(self):
        def _t():
            asyncio.set_event_loop(self._loop)
            self._loop.run_forever()

        t = threading.Thread(target=_t, daemon=True)
        t.start()
        if self._mesh_client:
            # ensure mesh client init success, and we will connect to mesh_service_address
            logger.debug("has mesh client, start a heartbeat thread")
            asyncio.run_coroutine_threadsafe(self._heartbeat_timer(self._get_address(None)), self._loop)
        logger.debug("client coro thread started")
        return t

    def invoke_oneway(self, interface, method, content, *, spanctx, **headers):
        header = SofaHeader.build_header(spanctx, interface, method, **headers)
        pkg = BoltRequest.new_request(header, content, timeout_ms=-1)
        asyncio.run_coroutine_threadsafe(self.invoke(pkg), loop=self._loop)

    def invoke_sync(self, interface, method, content, *, spanctx, timeout_ms, **headers):
        """blocking call to interface, returns responsepkg.content(as bytes)"""
        assert isinstance(timeout_ms, (int, float))
        header = SofaHeader.build_header(spanctx, interface, method, **headers)
        pkg = BoltRequest.new_request(header, content, timeout_ms=timeout_ms)
        fut = asyncio.run_coroutine_threadsafe(self.invoke(pkg), loop=self._loop)
        try:
            ret = fut.result(timeout=timeout_ms / 1000)
        except (TimeoutError, CancelledError) as e:
            logger.error("call to [{}:{}] timeout/cancelled. {}".format(interface, method, e))
            raise
        return ret.content

    def invoke_async(self, interface, method, content, *, spanctx, callback=None, timeout_ms=None, **headers):
        """
        call callback if callback is a callable,
        otherwise return a future
        Callback should recv a bytes object as the only argument, which is the response pkg's content
        """
        header = SofaHeader.build_header(spanctx, interface, method, **headers)
        pkg = BoltRequest.new_request(header, content, timeout_ms=timeout_ms or -1)
        fut = asyncio.run_coroutine_threadsafe(self.invoke(pkg), loop=self._loop)
        if callable(callback):
            fut.add_done_callback(self.callback_wrapper(callback, timeout_ms / 1000 if timeout_ms else None))
            return fut
        return fut

    @staticmethod
    def callback_wrapper(callback, timeout=None):
        """get future's result, then feed to callback"""

        @functools.wraps(callback)
        def _inner(fut):
            try:
                ret = fut.result(timeout)
            except (CancelledError, TimeoutError):
                logger.error("Failed to get result")
                return
            return callback(ret.content)

        return _inner

    async def _heartbeat_timer(self, address, interval=30):
        """Invoke heartbeat periodly"""
        while True:
            await asyncio.sleep(interval)
            await self.invoke_heartbeat(address)

    async def invoke_heartbeat(self, address):
        """
        Send heartbeat to server

        :return bool, if the server response properly.
        TODO: to break the connection if server response wrongly
        """
        pkg = HeartbeatRequest.new_request()
        resp = await self.invoke(pkg, address=address)
        if resp.request_id != pkg.request_id:
            logger.error("heartbeat response request_id({}) mismatch with request({}).".format(resp.request_id,
                                                                                               pkg.request_id))
            return False
        if resp.respstatus != RESPSTATUS.SUCCESS:
            logger.error("heartbeat response status ({}) on request({}).".format(resp.respstatus, resp.request_id))
            return False
        return True

    async def _get_connection(self, address):
        try:
            # fast path return existed connection
            if address in self.connection_mapping:
                return self.connection_mapping[address]

            async with self._pending_dial.setdefault(address, asyncio.Lock()):
                if address in self.connection_mapping:
                    return self.connection_mapping[address]

                reader, writer = await asyncio.open_connection(*address)
                task = asyncio.ensure_future(self._recv_response(reader, writer))
                return self.connection_mapping.setdefault(address, (task, writer))
        except Exception as e:
            logger.error("Get connection of {} failed: {}".format(address, e))
            raise

    async def invoke(self, request: BoltRequest, *, address=None):
        """
        A request response wrapper
        :param address: a inet address, currently only for heartbeat request
        """
        address = address or self._get_address(request.header['service'])
        logger.debug("invoke to address: {}".format(address))

        event = await self._send_request(request, address=address)
        if event is None:
            logger.debug("no related event, should be a async/oneway call, return now")
            return
        await event.wait()
        return self.response_mapping.pop(request.request_id)

    async def _send_request(self, request: BoltRequest, *, address):
        """
        send request and put request_id in request_mapping for response match
        :param request:
        :param address: a inet address, currently only for heartbeat request
        :return:
        """
        assert isinstance(request, BoltRequest)

        async def _send(retry=3):
            if retry <= 0:
                raise PyboltError("send request failed.")
            readtask, writer = await self._get_connection(address)
            try:
                await writer.drain()  # avoid back pressure
                writer.write(request.to_stream())
                await writer.drain()
            except Exception as e:
                logger.error("Request sent to {} failed: {}, may try again.".format(address, e))
                readtask.cancel()
                self.connection_mapping.pop(address)
                self._pending_dial.pop(address)
                await _send(retry - 1)

        # generate event object first, ensure every successfully sent request has a event
        self.request_mapping[request.request_id] = asyncio.Event()
        try:
            await _send()
        except PyboltError:
            logger.error("failed to send request {}".format(request.request_id))
            self.request_mapping.pop(request.request_id)
            return
        except Exception:
            logger.error(traceback.format_exc())
            self.request_mapping.pop(request.request_id)
            return

        if request.ptype == PTYPE.ONEWAY:
            self.request_mapping.pop(request.request_id)
            return

        return self.request_mapping[request.request_id]

    async def _recv_response(self, reader, writer):
        """
        wait response and put it in response_mapping, than notify the invoke coro
        :param reader:
        :return:
        """
        while True:
            pkg = None
            try:
                fixed_header_bs = await reader.readexactly(BoltResponse.bolt_header_size())
                header = BoltResponse.bolt_header_from_stream(fixed_header_bs)
                bs = await reader.readexactly(header['class_len'] + header['header_len'] + header['content_len'])
                pkg = BoltResponse.bolt_content_from_stream(bs, header)
                if pkg.class_name != BoltResponse.class_name:
                    raise ServerError("wrong class_name:[{}]".format(pkg.class_name))
                if pkg.cmdcode == CMDCODE.HEARTBEAT:
                    continue
                elif pkg.cmdcode == CMDCODE.REQUEST:
                    # raise error, the connection will be dropped
                    raise ServerError("wrong cmdcode:[{}]".format(pkg.cmdcode))
                if pkg.respstatus != RESPSTATUS.SUCCESS:
                    raise ServerError.from_statuscode(pkg.respstatus)
                if pkg.request_id not in self.request_mapping:
                    continue
                self.response_mapping[pkg.request_id] = pkg

            except PyboltError as e:
                logger.error(e)
            except (asyncio.CancelledError, EOFError, ConnectionResetError) as e:
                logger.error(e)
                writer.close()
                break
            except Exception:
                logger.error(traceback.format_exc())
                writer.close()
                break
            finally:
                with suppress(AttributeError, KeyError):
                    # wake up the coro
                    event = self.request_mapping.pop(pkg.request_id)
                    event.set()

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
   File Name : client
   Author : jiaqi.hjq
   Create Time : 2018/5/17 12:22
   Description : describe the main function of this file
   Change Activity:
        version0 : 2018/5/17 12:22 by jiaqi.hjq  init
"""
import logging
import time

try:
    from selectors import DefaultSelector, EVENT_READ
except ImportError:
    from selectors34 import DefaultSelector, EVENT_READ

from mysockpool import PoolManager

from anthunder.exceptions import ServerError
from anthunder.helpers.singleton import Singleton
from anthunder.protocol import BoltResponse, BoltRequest, SofaHeader
from anthunder.protocol.constants import PTYPE, RESPSTATUS
from .base import _BaseClient

logger = logging.getLogger(__name__)


class Client(_BaseClient):
    __metaclass__ = Singleton
    """
    Client Entrance

    Usage:
    Client(interface).sync(method, content, **kw)

    Need to keep the api stable
    """

    def _raw_invoke(self, interface, method_name, content, spanctx=None, target_app="", uid="",
                    timeout_ms=None, bolt_ptype=PTYPE.REQUEST, **sofa_headers_extra):

        """
        :param content:
        :param service:
        :param target_app:
        :param uid:
        :param rpc_trace_context: preserved, rpc_trace_context object, should be expanded as a dict like
                                  {'rpc_trace_context.traceId': 'xxxxx', ...}
        :param kwargs:
        """
        header = SofaHeader.build_header(spanctx, interface, method_name, target_app=target_app, uid=uid,
                                         **sofa_headers_extra)
        p = BoltRequest.new_request(header, content, timeout_ms=timeout_ms or -1, ptype=bolt_ptype)
        conn = self._get_pool(interface).get_conn()
        conn.send(p.to_stream())
        return p.request_id, conn

    def _get_pool(self, interface):
        return PoolManager().connection_pool_from_pool_key(
            PoolManager.PoolCls.ConnectionCls.PoolKeyCls(*self._get_address(interface)))

    def invoke_oneway(self, interface, method_name, content, spanctx=None, target_app="", uid=""):
        _, c = self._raw_invoke(interface, method_name, content, target_app=target_app, uid=uid,
                                spanctx=spanctx, bolt_ptype=PTYPE.ONEWAY)
        self._get_pool(interface).put_conn(c)

    def invoke_sync(self, interface, method_name, content, spanctx=None, target_app="", uid="", timeout_ms=None):
        """
        :param request:
        :param timeout: if timeout > 0, this specifies the maximum wait time, in
                   seconds
                   if timeout <= 0, the select() call won't block, and will
                   report the currently ready file objects
                   if timeout is None, select() will block until a monitored
                   file object becomes ready
        :return: serialized response content
        :raise: TimeoutError
        """
        assert isinstance(timeout_ms, (int, float))
        pkg = BoltResponse
        deadline = time.time() + timeout_ms / 1000 + 1
        req_id, c = self._raw_invoke(interface, method_name, content, target_app=target_app, uid=uid,
                                     spanctx=spanctx, timeout_ms=timeout_ms)

        with DefaultSelector() as sel:
            sel.register(c, EVENT_READ)
            total_size = pkg.bolt_header_size()
            resp_bytes = b''
            header = None
            while len(resp_bytes) < total_size:
                ready = sel.select(timeout=deadline - time.time())
                if not ready:
                    # timeout
                    c.close()
                    raise TimeoutError('Sync call timeout')
                for key, event in ready:
                    resp_bytes += key.fileobj.recv(total_size - len(resp_bytes))
                if not header and len(resp_bytes) >= total_size:
                    header = pkg.bolt_header_from_stream(resp_bytes)
                    body_size = header['class_len'] + header['header_len'] + header['content_len']
                    total_size += body_size
        self._get_pool(interface).put_conn(c)

        resp = pkg.bolt_content_from_stream(resp_bytes[pkg.bolt_header_size():], header)
        if resp.request_id != req_id:
            raise ServerError("RequestId not match")
        if resp.respstatus != RESPSTATUS.SUCCESS:
            raise ServerError.from_statuscode(resp.respstatus)
        return resp.content

    def invoke_async(self, interface, method_name, content, spanctx=None, callback=None, **kw):
        pass

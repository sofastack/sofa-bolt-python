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
   File Name : sock_listener.py
   Author : jiaqi.hjq
"""
import logging
import threading
import traceback
from errno import ECONNRESET
import six

if six.PY34:
    from socketserver import StreamRequestHandler, ThreadingTCPServer
else:
    from SocketServer import StreamRequestHandler, ThreadingTCPServer

import opentracing
from mytracer import tracer

from anthunder.command.fail_response import FailResponse
from anthunder.command.heartbeat import HeartbeatResponse
from anthunder.exceptions import ClientError
from anthunder.listener.aio_listener import NoProcessorError
from anthunder.protocol import BoltRequest, SofaHeader
from anthunder.protocol.constants import CMDCODE, RESPSTATUS

from .base_listener import BaseListener, BaseHandler

logger = logging.getLogger(__name__)


class BoltRequestHandler(StreamRequestHandler, BaseHandler):
    def _readexactly(self, bs_cnt):
        bs = b''
        while len(bs) < bs_cnt:
            bs += self.rfile.read(bs_cnt - len(bs))
        return bs

    def handle(self):
        try:
            fixed_header_bs = self._readexactly(BoltRequest.bolt_header_size())
            header = BoltRequest.bolt_header_from_stream(fixed_header_bs)
            call_type = header['ptype']
            cmdcode = header['cmdcode']

            class_name = self._readexactly(header['class_len'])
            bs = self._readexactly(header['header_len'])
            sofa_header = SofaHeader.from_bytes(bs)
            body = self._readexactly(header['content_len'])
            if self.server.ready:
                self.server.ready.set()

            request_id = header['request_id']

            if cmdcode == CMDCODE.HEARTBEAT:
                self.wfile.write(HeartbeatResponse.response_to(request_id).to_stream())
                self.wfile.flush()
                return

            if cmdcode == CMDCODE.RESPONSE:
                raise ClientError("wrong cmdcode:[{}]".format(cmdcode))

            if class_name != "com.alipay.sofa.rpc.core.request.SofaRequest".encode():
                raise ClientError("wrong class_name:[{}]".format(class_name))

            service = sofa_header.get('sofa_head_target_service') or sofa_header.get('service')
            if not service:
                self.wfile.write(FailResponse.response_to(request_id, RESPSTATUS.CLIENT_SEND_ERROR).to_stream())
                self.wfile.flush()
                logger.error("Missing service name in sofa header [{}]".format(sofa_header))
                return
            method = sofa_header.get('sofa_head_method_name')
            if not method:
                self.wfile.write(FailResponse.response_to(request_id, RESPSTATUS.CLIENT_SEND_ERROR).to_stream())
                self.wfile.flush()
                logger.error("Missing method name in sofa header [{}]".format(sofa_header))
                return

            spanctx = tracer.extract(opentracing.Format.TEXT_MAP, sofa_header)
            ret = self.handle_request(spanctx, service, method, body)
            self.wfile.write(ret)
            self.wfile.flush()

        except OSError as e:
            if e.errno != ECONNRESET:
                raise

        except Exception as e:
            logger.error(traceback.format_exc())

    def handle_request(self, spanctx, service, method, body):
        """blocking handles request"""
        try:
            ServiceCls = self.interface_mapping[service]
        except KeyError as e:
            logger.error("Service not found in interface registry: [{}]".format(service))
            raise NoProcessorError("Service not found in interface registry: [{}]".format(service))
        try:
            svc_obj = ServiceCls(spanctx)
            func = getattr(svc_obj, method)
        except AttributeError as e:
            logger.error("No such method[{}]".format(method))
            raise NoProcessorError("No such method[{}]".format(method))

        return func(body)

    def register_interface(self, interface, service_cls):
        self.interface_mapping[interface] = service_cls


class SockListener(BaseListener):
    ServerCls = ThreadingTCPServer
    HandlerCls = BoltRequestHandler

    def __init__(self, *args, **kwargs):
        super(SockListener, self).__init__(*args, **kwargs)
        self.server = self.ServerCls(self.address, self.HandlerCls)

    def run_forever(self):
        self.server.serve_forever()

    def shutdown(self):
        self.server.shutdown()

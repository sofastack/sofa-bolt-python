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
   File Name : _request_pkg
   Author : jiaqi.hjq
   Create Time : 2018/4/28 11:39
   Description : description what the main function of this file
   Change Activity:
        version0 : 2018/4/28 11:39 by jiaqi.hjq  init
"""
import struct
from anthunder.helpers.request_id import RequestId
from .constants import PTYPE, CMDCODE
from .exceptions import EncodeError
from ._package_base import BoltPackage


class BoltRequest(BoltPackage):
    fmt = "!bbhblblHHL"
    class_name = b"com.alipay.sofa.rpc.core.request.SofaRequest"
    bolt_headers = ("proto", "ptype", "cmdcode", "ver2", "request_id", "codec", "timeout",
                    "class_len", "header_len", "content_len")

    def to_stream(self):
        self.validate()
        try:
            bodyfmt = "%ds%ds%ds" % (self.class_len, self.header_len, self.content_len)
            return struct.pack(self.fmt + bodyfmt, self.proto, self.ptype, self.cmdcode,
                               self.ver2, self.request_id, self.codec, self.timeout,
                               self.class_len, self.header_len, self.content_len,
                               self.class_name, self._header_bytes, self.content)
        except Exception as e:  # pragma: no cover
            raise EncodeError(e)

    @classmethod
    def new_request(cls, header, content, ptype=PTYPE.REQUEST, timeout_ms=None, **kwargs):
        return cls(header, content, ptype=ptype, cmdcode=CMDCODE.REQUEST,
                   request_id=next(RequestId), timeout=timeout_ms or -1, **kwargs)

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
   File Name : header
   Author : jiaqi.hjq
   Create Time : 2018/5/17 14:04
   Description : describe the main function of this file
   Change Activity:
        version0 : 2018/5/17 14:04 by jiaqi.hjq  init
"""
import struct
from mytracer import SpanContext

from ._rpc_trace_context import RpcTraceContext
from .exceptions import EncodeError, DecodeError


def _int2bytes_be(i):
    return struct.pack('>i', i)


def _bytes2int_be(bs):
    i, = struct.unpack('>i', bs)
    return i


def _str_to_bytes_with_len(s, coding='utf-8'):
    """
    a simple str serialize method

    java's writeInt writes 4 bytes in 'high bytes first' according to its documents

    :param s:
    :param coding:
    :return: bytes object
    """
    assert isinstance(s, str)
    b = s.encode(coding)
    return _int2bytes_be(len(b)) + b


def _bytes_to_str(b, coding='utf-8'):
    """
    a simple str unserialize method

    java's writeInt writes 4 bytes in 'high bytes first' according to its documents

    :param b:
    :param coding:
    :return: list of str
    """

    assert isinstance(b, bytes)
    ret = []
    while b:
        if 4 > len(b):  # pragma: no cover
            raise DecodeError('decoding bytes to int failed, not enough length')
        l = _bytes2int_be(b[:4])  # length
        n = 4 + l  # next point
        if n > len(b):  # pragma: no cover
            # incomplete bytes
            raise DecodeError('decoding bytes to str failed, not enough length')
        ret.append(b[4: n].decode(coding))
        b = b[n:]

    return ret


class SofaHeader(dict):
    """
    Readonly dict, with special serialize method
    """

    def __setitem__(self, key, value):  # pragma: no cover
        pass

    @classmethod
    def from_bytes(cls, b):
        ss = _bytes_to_str(b)
        keys = ss[::2]
        vals = ss[1::2]
        if len(keys) != len(vals):  # pragma: no cover
            raise DecodeError('number of keys and values not match')
        return cls(zip(keys, vals))

    def to_bytes(self):
        return bytes(self)

    def __bytes__(self):
        try:
            return b''.join(_str_to_bytes_with_len(k) + _str_to_bytes_with_len(v) for k, v in self.items())
        except AttributeError as e:  # pragma: no cover
            raise EncodeError(e)

    def __len__(self):
        return len(self.to_bytes())

    @classmethod
    def build_header(cls, spanctx, interface, method_name, target_app="", uid="",
                     **sofa_headers_extra):
        """
        :param spanctx:
        :type spanctx: SpanContext
        :param interface:
        :param method_name:
        :param target_app:
        :param uid:
        :param sofa_headers_extra:
        :return:
        """
        rpc_trace_context_expand = RpcTraceContext(**spanctx.baggage).expand()

        kwargs = dict()
        kwargs.update(**sofa_headers_extra)
        kwargs.update(**rpc_trace_context_expand)

        header = cls(sofa_head_target_service=interface,
                     sofa_head_method_name=method_name,
                     sofa_head_target_app=target_app,
                     service=interface,
                     uid=uid, **kwargs)
        return header


empty_header = SofaHeader()

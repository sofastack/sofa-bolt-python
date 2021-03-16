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
   Create Time : 2021/3/16 11:39
   Description : description what the main function of this file
   Change Activity:
        version0 : 2021/3/16 11:39 by jiaqi.hjq  init
"""
from anthunder.protocol.constants import CODEC


class Codecoder():
    """
    Codecoder is class combines codec and its de/serialize functions.
    """
    def __init__(self, codec, serialize, deserialize):
        """
        :param codec: int, normally should be CODEC defined in constants.
        :param serialize: callable, serialize function for codec.
        :param deserialize: callable, deserialize function for codec.
        """
        self.codec = codec
        self.serialize = serialize
        self.deserialize = deserialize


class Payload(object):
    """
    Insead of raw bytes, Payload object provides a way to support more adjective objects passing 
    through client and/or listener. For now, Payload is mainly for supporting other serializer besides protobuf.
    """
    def __init__(self, payload, codec: Codecoder):
        """
        init accept payload objects and save them as self.payload
        For sending payload, object should be un-serialized.
        For receiving payload, object should be bytes, and wait for deserialize.
        """
        self.payload = payload
        self._c = codec

    @property
    def codec(self) -> int:
        """
        codec must be attribute/property. The value of codec must be an int, normally should be CODEC defined in constants.
        If codec is not defined, then CODEC.PROTOBUF is used.
        """
        return self._c.codec

    def serialize(self) -> bytes:
        """
        method to serialize payload
        """
        return self._c.serialize(self.payload)

    def deserialize(self) -> object:
        """
        method to deserialize payload
        """
        return self._c.deserialize(self.payload)


# HessianCodec = Codecoder(CODEC.HESSIAN, )


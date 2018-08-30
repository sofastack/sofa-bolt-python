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
   File Name : constants
   Author : jiaqi.hjq
   Create Time : 2018/4/28 11:47
   Description : description what the main function of this file
   Change Activity:
        version0 : 2018/4/28 11:47 by jiaqi.hjq  init
"""
from enum import Enum


class PROTO(Enum):
    BOLT = 1


class PTYPE(Enum):
    RESPONSE = 0
    REQUEST = 1
    ONEWAY = 2


class CMDCODE(Enum):
    HEARTBEAT = 0
    REQUEST = 1
    RESPONSE = 2


class VER2(Enum):
    REMOTING = 1


class CODEC(Enum):
    HESSIAN = 1
    PROTOBUF = 11
    JAVA = 2


class RESPSTATUS(Enum):
    SUCCESS = 0x0000
    ERROR = 0x0001
    SERVER_EXCEPTION = 0x0002
    UNKNOWN = 0x0003
    SERVER_THREADPOOL_BUSY = 0x0004
    ERROR_COMM = 0x0005
    NO_PROCESSOR = 0x0006
    TIMEOUT = 0x0007
    CLIENT_SEND_ERROR = 0x0008
    CODEC_EXCEPTION = 0x0009
    CONNECTION_CLOSED = 0x0010
    SERVER_SERIAL_EXCEPTION = 0x0011
    SERVER_DESERIAL_EXCEPTION = 0x0012

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
   File Name : trace_id
   Author : jiaqi.hjq
   Create Time : 2018/5/28 14:00
   Description : describe the main function of this file
   Change Activity:
        version0 : 2018/5/28 14:00 by jiaqi.hjq  init
"""
import itertools
import os
import socket
import time
import ipaddress
import six


class TraceId(object):
    _sequence = itertools.cycle(range(1000, 9001))

    def __init__(self, trace=None):
        if not isinstance(trace, str):
            _ip = int(ipaddress.ip_address(six.u(socket.gethostbyname(socket.gethostname()))))
            _ts = int(time.time() * 1000)
            _sq = next(self._sequence)
            _pid = os.getpid()
            self._trace_id = "{:0>8x}{:}{}{}".format(_ip, _ts, _sq, _pid)
        else:
            self._trace_id = trace

    def __str__(self):
        return self._trace_id

    __repr__ = __str__

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        return self._trace_id == other._trace_id

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

    Original Copyright 2008-2016 Andrey Petrov and contributors
    (see https://github.com/urllib3/urllib3/blob/master/CONTRIBUTORS.txt)
    under the MIT license (https://opensource.org/licenses/MIT).
   ------------------------------------------------------
   File Name : connection.py
"""
import socket
from collections import namedtuple
from io import BytesIO

from .exceptions import LocationValueError
from ._wait import wait_for_write, wait_for_read


class SocketConnection(object):
    PoolKeyCls = namedtuple('SocketPoolKey', ('host', 'port'))

    def __init__(self, pool_key, blocking=False, **kwargs):
        self.validate_pool_key(pool_key)
        self.pool_key = pool_key
        sock = socket.socket(socket.AF_INET)
        sock.setblocking(blocking)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
        try:
            sock.connect((pool_key.host, pool_key.port))
        except:
            pass
        self.sock = sock

    @classmethod
    def validate_pool_key(cls, pool_key):
        if not isinstance(pool_key, cls.PoolKeyCls):
            raise LocationValueError("Invalid pool_key object for creating new connection.")

    def close(self):
        try:
            self.sock.close()
        except:
            pass

    def send(self, *args, **kw):
        wait_for_write(self.sock)
        return self.sock.send(*args, **kw)

    def sendall(self, *args, **kw):
        wait_for_write(self.sock)
        return self.sock.sendall(*args, **kw)

    def recv(self, *args, **kw):
        return self.sock.recv(*args, **kw)

    def recvexactly(self, size):
        read = 0
        buf = BytesIO()
        while read < size:
            wait_for_read(self.sock)
            bs = self.sock.recv(size - read)
            buf.write(bs)
            read += len(bs)
        return buf.getvalue()

    def fileno(self):
        return self.sock.fileno()

    def __del__(self):
        self.close()

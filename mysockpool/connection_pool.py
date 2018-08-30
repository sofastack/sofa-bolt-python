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
   File Name : connection_pool
"""
import logging

try:
    import queue
except ImportError:
    # python2.7
    import Queue as queue
import threading

from .connection import SocketConnection
from .exceptions import LocationValueError, ClosedPoolError, EmptyPoolError
from .utils import is_connection_dropped

log = logging.getLogger(__name__)


# Pool objects
class ConnectionPool(object):
    """
    Base class for all connection pools, such as
    :class:`.HTTPConnectionPool` and :class:`.HTTPSConnectionPool`.
    """

    QueueCls = queue.LifoQueue
    ConnectionCls = SocketConnection

    def __init__(self, pool_key,
                 initial_connections=1,
                 max_connections=20,
                 max_free_connections=5,
                 min_free_connections=1,
                 block=False,
                 ):
        if not pool_key:
            raise LocationValueError("No pool_key specified.")

        self._lock = threading.RLock()

        self.ConnectionCls.validate_pool_key(pool_key)
        self.pool_key = pool_key

        self.block = block
        self.num_connections = 0
        self.min_free_connections = min_free_connections
        self.max_connections = max_connections

        self.pool = self.QueueCls(max_free_connections)
        for i in range(initial_connections):
            self.pool.put(self._new_conn())

    def __str__(self):
        return '%s(%r)' % (type(self).__name__, self.pool_key)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
        # Return False to re-raise any potential exceptions
        return False

    def _new_conn(self):
        with self._lock:
            if self.num_connections >= self.max_connections:
                raise EmptyPoolError(self,
                                     "Pool reached maximum size and no more "
                                     "connections are allowed.")

        self.num_connections += 1
        log.debug("Starting new connection (%d): %r",
                  self.num_connections, self.pool_key)

        conn = self.ConnectionCls(self.pool_key)
        return conn

    def get_conn(self, timeout=None):
        """
        Get a connection. Will return a pooled connection if one is available.

        If no connections are available and :prop:`.block` is ``False``, then a
        fresh connection is returned.

        :param timeout:
            Seconds to wait before giving up and raising
            :class:`urllib3.exceptions.EmptyPoolError` if the pool is empty and
            :prop:`.block` is ``True``.
        """
        conn = None
        try:
            conn = self.pool.get(block=self.block, timeout=timeout)

            if self.pool.qsize() < self.min_free_connections:
                self.put_conn(self._new_conn())

        except AttributeError:  # self.pool is None
            raise ClosedPoolError(self, "Pool is closed.")

        except queue.Empty:
            if self.block:
                raise EmptyPoolError(self,
                                     "Pool reached maximum size and no more "
                                     "connections are allowed.")
            pass  # Oh well, we'll create a new connection then

        # If this is a persistent connection, check if it got disconnected
        if conn and is_connection_dropped(conn):
            log.debug("Resetting dropped connection: %r", self.pool_key)
            conn.close()
            with self._lock:
                self.num_connections -= 1

        return conn or self._new_conn()

    def put_conn(self, conn):
        """
        Put a connection back into the pool.

        :param conn:
            Connection object for the current host and port as returned by
            :meth:`._new_conn` or :meth:`._get_conn`.

        If the pool is already full, the connection is closed and discarded
        because we exceeded maxsize. If connections are discarded frequently,
        then maxsize should be increased.

        If the pool is closed, then the connection will be closed and discarded.
        """
        try:
            self.pool.put(conn, block=False)
            return  # Everything is dandy, done.
        except AttributeError:
            # self.pool is None.
            pass
        except queue.Full:
            # This should never happen if self.block == True
            log.warning(
                "Connection pool is full, discarding connection: %s",
                self.pool_key)
            with self._lock:
                self.num_connections -= 1

        # Connection never got put back into the pool, close it.
        if conn:
            conn.close()

    def close(self):
        """
        Close all pooled connections and disable the pool.
        """
        # Disable access to the pool
        old_pool, self.pool = self.pool, None

        try:
            while True:
                conn = old_pool.get(block=False)
                if conn:
                    conn.close()

        except queue.Empty:
            pass  # Done.

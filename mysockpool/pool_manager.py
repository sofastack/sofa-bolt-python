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
   File Name : pool_manager
"""
from contextlib import contextmanager

from .recently_used_container import RecentlyUsedContainer
from .connection_pool import ConnectionPool


class PoolManager(object):
    """
    Allows for arbitrary requests while transparently keeping track of
    necessary connection pools for you.

    :param num_pools:
        Number of connection pools to cache before discarding the least
        recently used pool.

    :param \\**connection_pool_kw:
        Additional parameters are used to create fresh
        :class:`urllib3.connectionpool.ConnectionPool` instances.
    """

    PoolCls = ConnectionPool

    def __init__(self, max_pools=10, **pool_kwargs):
        self.pool_kwargs = pool_kwargs
        self.pools = RecentlyUsedContainer(max_pools,
                                           dispose_func=lambda p: p.close())

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.clear()
        # Return False to re-raise any potential exceptions
        return False

    def _new_pool(self, pool_key):
        """
        Create a new :class:`ConnectionPool` based on host, port, scheme, and
        any additional pool keyword arguments.

        If ``request_context`` is provided, it is provided as keyword arguments
        to the pool class used. This method is used to actually create the
        connection pools handed out by :meth:`connection_from_url` and
        companion methods. It is intended to be overridden for customization.
        """
        return self.PoolCls(pool_key, **self.pool_kwargs)

    def clear(self):
        """
        Empty our store of pools and direct them all to close.

        This will not affect in-flight connections, but they will not be
        re-used after completion.
        """
        self.pools.clear()

    def connection_pool_from_pool_key(self, pool_key):
        """
        Get a :class:`ConnectionPool` based on the provided pool key.

        ``pool_key`` should be a namedtuple that only contains immutable
        objects. At a minimum it must have the ``scheme``, ``host``, and
        ``port`` fields.
        """
        with self.pools.lock:
            # If the scheme, host, or port doesn't match existing open
            # connections, open a new ConnectionPool.
            pool = self.pools.get(pool_key)
            if pool:
                return pool

            # Make a fresh ConnectionPool of the desired type
            pool = self._new_pool(pool_key)
            self.pools[pool_key] = pool

        return pool

    @contextmanager
    def connection_scope(self, pool_key):
        try:
            pool = self.connection_pool_from_pool_key(pool_key)
            conn = pool.get_conn()
            yield conn
        except:
            raise
        finally:
            try:
                pool.put_conn(conn)
            except (NameError, AttributeError):
                pass

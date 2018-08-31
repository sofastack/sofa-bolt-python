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
   File Name : test_connection
   Author : jiaqi.hjq
"""
import unittest

try:
    from unittest import mock
except ImportError:
    import mock

from mysockpool.connection import SocketConnection
from mysockpool.connection_pool import ConnectionPool
from mysockpool.exceptions import EmptyPoolError
from mysockpool.pool_manager import PoolManager


class TestPoolManager(unittest.TestCase):
    def test_pool_man(self):
        poolman = PoolManager(2)
        conn0 = poolman.connection_pool_from_pool_key(
            poolman.PoolCls.ConnectionCls.PoolKeyCls(host='127.0.0.1', port=8080))
        self.assertEqual(len(poolman.pools), 1)
        conn1 = poolman.connection_pool_from_pool_key(
            poolman.PoolCls.ConnectionCls.PoolKeyCls(host='127.0.0.1', port=8081))
        self.assertEqual(len(poolman.pools), 2)
        conn2 = poolman.connection_pool_from_pool_key(
            poolman.PoolCls.ConnectionCls.PoolKeyCls(host='127.0.0.1', port=8082))
        # should be limited to 2
        self.assertEqual(len(poolman.pools), 2)
        conn11 = poolman.connection_pool_from_pool_key(
            poolman.PoolCls.ConnectionCls.PoolKeyCls(host='127.0.0.1', port=8081))
        # Same one
        self.assertIs(conn11, conn1)
        conn01 = poolman.connection_pool_from_pool_key(
            poolman.PoolCls.ConnectionCls.PoolKeyCls(host='127.0.0.1', port=8080))
        # Not the same one
        self.assertIsNot(conn01, conn0)
        self.assertIsNotNone(conn01.pool)
        self.assertIsNone(conn0.pool)

    def test_pool_conn_scope(self):
        poolman = PoolManager(2, initial_connections=2)
        pool_key = poolman.PoolCls.ConnectionCls.PoolKeyCls(host='127.0.0.1', port=8080)
        pool = poolman.connection_pool_from_pool_key(pool_key)
        before = pool.num_connections

        with poolman.connection_scope(pool_key) as conn:
            self.assertEqual(before - 1, pool.pool.qsize())
        self.assertEqual(before, pool.pool.qsize())

    @mock.patch("mysockpool.connection_pool.is_connection_dropped",
                mock.MagicMock(return_value=False))
    def test_pool(self):
        class Handler(object):
            def __init__(self, *args, **kwargs):
                pass

        pool_key = SocketConnection.PoolKeyCls(host='localhost', port=8081)
        pool = ConnectionPool(pool_key, max_connections=10, max_free_connections=4, min_free_connections=2,
                              initial_connections=3)
        self.assertEqual(3, pool.num_connections)
        self.assertEqual(3, pool.pool.qsize())
        c0 = pool.get_conn()
        self.assertEqual(3, pool.num_connections)
        self.assertEqual(2, pool.pool.qsize())
        c1 = pool.get_conn()
        self.assertEqual(4, pool.num_connections)
        self.assertEqual(2, pool.pool.qsize())

        conns = [pool.get_conn() for i in range(6)]
        with self.assertRaises(EmptyPoolError):
            c2 = pool.get_conn()
        print(len(conns))
        self.assertEqual(10, pool.num_connections)
        [pool.put_conn(conn) for conn in conns]

        self.assertEqual(7, pool.num_connections)

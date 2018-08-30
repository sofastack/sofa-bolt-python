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
   File Name : test_client
   Author : jiaqi.hjq
   Create Time : 2018/5/18 11:19
   Description : describe the main function of this file
   Change Activity:
        version0 : 2018/5/18 11:19 by jiaqi.hjq  init
"""
import unittest


class TestClient(unittest.TestCase):
    def test_client_get_address(self):
        from anthunder.client.base import _BaseClient
        addr = _BaseClient("anthunderTestApp")._get_address("com.alipay.rpc.no_such_service")
        print(addr)
        self.assertEqual(addr, ('127.0.0.1', 12220))

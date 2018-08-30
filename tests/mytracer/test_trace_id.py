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
   File Name : test_trace_id
   Author : jiaqi.hjq
   Create Time : 2018/5/28 14:00
   Description : describe the main function of this file
   Change Activity:
        version0 : 2018/5/28 14:00 by jiaqi.hjq  init
"""
import unittest

from mytracer._rpc_id import RpcId
from mytracer._trace_id import TraceId


class TestTraceId(unittest.TestCase):
    def test_trace_id(self):
        self.assertNotEqual(str(TraceId()), str(TraceId()))
        id = TraceId()
        print(str(id))

    def test_rpc_id(self):
        sid = RpcId()
        print(sid)
        self.assertEqual(str(sid), '1')
        self.assertEqual(sid, RpcId(1))
        sid = sid._new_follows_from()
        print(sid)
        self.assertEqual(str(sid), '2')
        sid = sid._new_child_of()
        self.assertEqual(str(sid), '2.1')

        self.assertNotEqual(RpcId(1, 1), RpcId(1, 1, 1))
        self.assertNotEqual(RpcId(1), 1)
        self.assertNotEqual(RpcId(1, 1, 2), RpcId(1, 1, 1))

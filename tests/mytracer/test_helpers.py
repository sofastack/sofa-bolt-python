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
   File Name : test_helpers
   Author : jiaqi.hjq
"""
import time
import unittest

import opentracing
from opentracing import Reference, ReferenceType

from mytracer._rpc_id import RpcId
from mytracer._trace_id import TraceId
from mytracer.helpers import new_span, child_span_of, follows_span_from
from mytracer.tracer import MyTracer


class TestHelpers(unittest.TestCase):
    def test_new_span(self):
        with new_span("new_span") as span:
            # 1
            self.assertEqual(span.operation_name, "new_span")
            self.assertEqual(span.get_baggage_iterm("sofaRpcId"), RpcId(1))

            with child_span_of(span) as cspan:
                # 1.1
                print(cspan.context)
                self.assertEqual(cspan.operation_name, "new_span")
                self.assertEqual(cspan.get_baggage_iterm("sofaRpcId"), RpcId(1, 1))
                with follows_span_from(cspan, "follow_span") as fspan:
                    # 1.2
                    self.assertEqual(fspan.operation_name, "follow_span")
                    self.assertEqual(fspan.get_baggage_iterm("sofaRpcId"), RpcId(1, 2))

            with follows_span_from(span, "follow_span") as fspan:
                # 2
                self.assertEqual(fspan.operation_name, "follow_span")
                self.assertEqual(fspan.get_baggage_iterm("sofaRpcId"), RpcId(2))

            with child_span_of(span, "child_span") as cspan:
                # 1.3
                print(cspan.context)
                self.assertEqual(cspan.operation_name, "child_span")
                self.assertEqual(cspan.get_baggage_iterm("sofaRpcId"), RpcId(1, 3))

    def test_exception_barrier(self):
        with self.assertRaises(Exception):
            with new_span("new2") as span:
                raise Exception("")

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
   File Name : test_tracer
   Author : jiaqi.hjq
"""
import time
import unittest

import opentracing
from opentracing import Reference, ReferenceType

from mytracer._rpc_id import RpcId
from mytracer._trace_id import TraceId
from mytracer.tracer import MyTracer


class TestTracer(unittest.TestCase):
    def test_start_span(self):
        span = MyTracer().start_span("test_ops", start_time=time.time())
        print(str(span.context))
        self.assertEqual(span.get_baggage_iterm('sofaRpcId'), RpcId(1))

        childspan = MyTracer().start_span("test_ops", child_of=span)
        print(str(childspan.context))
        self.assertEqual(span.get_baggage_iterm('sofaTraceId'), childspan.get_baggage_iterm('sofaTraceId'))
        self.assertEqual(childspan.get_baggage_iterm('sofaRpcId'), RpcId(1, 1))

        followspan = MyTracer().start_span("test_ops", references=Reference(ReferenceType.FOLLOWS_FROM,
                                                                            childspan.context))
        print(str(followspan.context))
        self.assertEqual(span.get_baggage_iterm('sofaTraceId'), followspan.get_baggage_iterm('sofaTraceId'))
        self.assertEqual(followspan.get_baggage_iterm('sofaRpcId'), RpcId(1, 2))

    def test_extract_inject(self):
        carrier = {"rpc_trace_context.test": "value1",
                   "rpc_trace_context.sofaTraceId": "testTId",
                   "rpc_trace_context.sofaRpcId": "1.1",
                   "pc_trace_context.sofaRpcId": "testRId",
                   }
        spanctx = MyTracer().extract(opentracing.Format.TEXT_MAP, carrier)
        self.assertEqual(spanctx.baggage['sofaRpcId'], RpcId(1, 1))
        self.assertEqual(spanctx.baggage['sofaTraceId'], TraceId("testTId"))

        print(str(spanctx))

        with MyTracer().start_span("test_ops2", child_of=spanctx) as childspan:
            carrier = dict()
            MyTracer().inject(childspan.context, opentracing.Format.TEXT_MAP, carrier)
            print(carrier)
        print(str())

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
   File Name : test_server
   Author : jiaqi.hjq
"""
import unittest
import six
import logging

from anthunder.command.heartbeat import HeartbeatRequest, HeartbeatResponse
from anthunder.protocol.constants import RESPSTATUS

logger = logging.getLogger(__name__)

if six.PY34:
    import asyncio
    import concurrent.futures
    import functools
    import threading
    import time
    from unittest import mock
    from random import randint

    from mytracer import SpanContext

    from anthunder import AioClient
    from anthunder.listener.aio_listener import AioListener
    from anthunder.listener.base_listener import BaseService
    from tests.proto.python import SampleService
    from tests.proto.python.SampleServicePbRequest_pb2 import SampleServicePbRequest
    from tests.proto.python.SampleServicePbResult_pb2 import SampleServicePbResult


@unittest.skipUnless(six.PY34, "Aio-classes only support python>3.4")
class TestListener(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        lsn = AioListener(('127.0.0.1', 12200), "test_app")
        lsn.run_threading()
        cls.listener = lsn
        cls.interface = "com.alipay.rpc.common.service.facade.pb.SampleServicePb:1.0"
        time.sleep(0.1)

        class TestSampleServicePb(BaseService):
            def hello(self, bs):
                # add a delay
                time.sleep(randint(50, 300) / 1000)

                obj = SampleServicePbRequest()
                obj.ParseFromString(bs)
                print("Processing Request", obj)
                return SampleServicePbResult(result=obj.name).SerializeToString()

        cls.listener.handler.register_interface(cls.interface, TestSampleServicePb)

    def test_server(self):
        # mocked, will call to localhost
        with mock.patch.object(SampleService, "SERVICE_MAP", dict()):
            threading.Thread(target=SampleService.SampleService(SpanContext()).hello,
                             kwargs=dict(name="abcde-test0")).start()
            result = SampleService.SampleService(SpanContext()).hello(name="abcde-test")

            print(result)
        self.assertEqual(result.result, "abcde-test")

    def test_aio_client(self):
        client = AioClient("anthunderTestApp")
        _result = list()
        _ts = list()

        def _call(name):
            content = client.invoke_sync(self.interface, "hello",
                                         SampleServicePbRequest(name=str(name)).SerializeToString(),
                                         timeout_ms=5000, spanctx=SpanContext())
            result = SampleServicePbResult()
            result.ParseFromString(content)
            print(result.result == str(name))
            _result.append(result.result == str(name))

        for i in range(10):
            t = threading.Thread(target=_call, args=(i,))
            t.start()
            _ts.append(t)

        for t in _ts:
            t.join()

        self.assertEqual(len(_result), 10)
        self.assertTrue(all(_result))

    def test_heartbeat(self):
        pkg = HeartbeatRequest.new_request()
        print(pkg.to_stream())
        from socket import socket
        with socket() as s:
            s.connect(('127.0.0.1', 12200))
            s.send(pkg.to_stream())
            buf = b''
            buf += s.recv(1024)
            print(len(buf))
            print(buf)

        resp = HeartbeatResponse.from_stream(buf)
        print(resp)

        self.assertEqual(resp.request_id, pkg.request_id)
        self.assertEqual(resp.respstatus, RESPSTATUS.SUCCESS)

    def test_aio_client_async(self):
        print("async client")
        client = AioClient("anthunderTestApp")
        _result = list()

        def _cb(content, expect):
            result = SampleServicePbResult()
            result.ParseFromString(content)
            print(expect == result.result)
            _result.append(expect == result.result)

        def _acall(name):
            return client.invoke_async(self.interface, "hello",
                                       SampleServicePbRequest(name="async" + str(name)).SerializeToString(),
                                       timeout_ms=500, callback=functools.partial(_cb, expect="async" + str(name)),
                                       spanctx=SpanContext())

        fs = [_acall(i) for i in range(10)]
        concurrent.futures.wait(fs, timeout=1.5)
        time.sleep(0.1)
        self.assertEqual(len(_result), 10)
        self.assertTrue(all(_result))

    @classmethod
    def tearDownClass(cls):
        cls.listener.shutdown()


if __name__ == '__main__':
    unittest.main()

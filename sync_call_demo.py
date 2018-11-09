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
   File Name : demo.py
   Author : jiaqi.hjq
"""
import logging

from mytracer import SpanContext

logging.basicConfig()

from multiprocessing import Process
import time
from random import randint

try:
    from anthunder import AioListener as Listener, AioClient as Client
except ImportError:
    from anthunder import SockListener as Listener, Client
from anthunder import BaseService, SERVICE_MAP

from tests.proto.python.SampleServicePbRequest_pb2 import SampleServicePbRequest
from tests.proto.python.SampleServicePbResult_pb2 import SampleServicePbResult

localaddress = ('127.0.0.1', 12200)
interface = "com.alipay.rpc.common.service.facade.pb.SampleServicePb:1.0"
SERVICE_MAP[interface] = localaddress


def run_server():
    listener = Listener(localaddress, "test_app")
    time.sleep(0.1)

    class TestSampleServicePb(BaseService):
        def hello(self, bs):
            # add a delay
            time.sleep(randint(50, 300) / 100)

            obj = SampleServicePbRequest()
            obj.ParseFromString(bs)
            print("server: Processing request", obj)
            return SampleServicePbResult(result=obj.name).SerializeToString()

    listener.handler.register_interface(interface, TestSampleServicePb)

    listener.run_forever()


def run_client(text):
    print("client start", text)
    spanctx = SpanContext()

    client = Client("test_app")
    client.subscribe(interface)

    content = client.invoke_sync(interface, "hello",
                                 SampleServicePbRequest(name=text).SerializeToString(),
                                 timeout_ms=5000, spanctx=spanctx)
    print("client", content)
    result = SampleServicePbResult()
    result.ParseFromString(content)

    print("client", result)


print("starting server")
server_proc = Process(target=run_server)
server_proc.start()
time.sleep(1)

print("starting client")
run_client("client1")
run_client("client2")
run_client("client3")

server_proc.terminate()

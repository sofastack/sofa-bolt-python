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

from multiprocessing import Process, freeze_support
import time
from random import randint

from anthunder import AioListener as Listener, AioClient
from anthunder import BaseService
from anthunder.discovery import LocalRegistry
from anthunder.model import ProviderMetaInfo, SubServiceMeta

from tests.proto.python.SampleServicePbRequest_pb2 import SampleServicePbRequest
from tests.proto.python.SampleServicePbResult_pb2 import SampleServicePbResult


# Here we use LocalRegistry with local address for test purposes.
# see sample script in README for using MosnClient for service discovery
localaddress = '127.0.0.1:12200'
localinterface = "com.alipay.rpc.common.service.facade.pb.SampleServicePb:1.0"
provider = ProviderMetaInfo(appName="test_app")
registry = LocalRegistry({localinterface: SubServiceMeta(localaddress, provider)})


class TestSampleServicePb(BaseService):
    def __init__(self, ctx, *, server_name):
        super().__init__(ctx)
        self._name = server_name

    def hello(self, bs):
        # add a delay
        time.sleep(randint(50, 300) / 100)

        obj = SampleServicePbRequest()
        obj.ParseFromString(bs)
        print("server: Processing request", obj)
        # reference a pre init member
        ret = obj.name + self._name
        return SampleServicePbResult(result=ret).SerializeToString()


def run_server():

    listener = Listener(localaddress, "test_app")
    time.sleep(0.1)

    # some initialize work
    server_name = "A_DYNAMIC_NAME"

    listener.register_interface(
        localinterface,
        provider_meta=provider,
        service_cls=TestSampleServicePb,
        service_cls_kwargs={"server_name": server_name})

    listener.run_forever()


class ServiceProvider(object):
    def __init__(self, client):
        self._client = client

    def hello(self, spanctx):
        self._client.invoke_sync(spanctx)


def run_client(text):
    print("client start", text)
    spanctx = SpanContext()

    client = AioClient("test_app", service_register=registry)

    content = client.invoke_sync(
        localinterface,
        "hello",
        SampleServicePbRequest(name=text).SerializeToString(),
        timeout_ms=5000,
        spanctx=spanctx)
    print("client", content)
    result = SampleServicePbResult()
    result.ParseFromString(content)

    print("client", result)


if __name__ == "__main__":
    freeze_support()

    print("starting server")
    server_proc = Process(target=run_server)
    server_proc.start()
    time.sleep(1)

    print("starting client")
    run_client("client1")
    run_client("client2")
    run_client("client3")

    server_proc.terminate()

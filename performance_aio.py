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
   File Name : performance
   Author : jiaqi.hjq
"""
import os

# os.environ["PYTHONASYNCIODEBUG"] = "1"
import asyncio
import logging
import threading

from concurrent.futures import ProcessPoolExecutor, wait

from mytracer import SpanContext

from anthunder import AioListener, BaseService, AioClient
from tests.proto.python.SampleServicePbRequest_pb2 import SampleServicePbRequest
from tests.proto.python.SampleServicePbResult_pb2 import SampleServicePbResult

logger = logging.getLogger(__name__)

interface = "com.alipay.rpc.common.service.facade.pb.SampleServicePb:1.0"


##########
# server process

class Counter(object):
    def __init__(self):
        self.count = 0
        self._lock = threading.RLock()

    def inc(self):
        self.count += 1

    async def print_count(self):
        secs = 0
        last_count = 0
        while True:
            await asyncio.sleep(1)
            secs += 1
            curr_count = self.count
            print("{} secs: {} requests: {} r/s".format(secs, curr_count, (curr_count - last_count)))
            last_count = curr_count


counter = Counter()


class CoroExecutor(object):
    def __init__(self, max_worker=None):
        pass

    def submit(self, func, *args, **kwargs):
        return asyncio.ensure_future(self._coro_wrapper(func, *args, **kwargs))

    async def _coro_wrapper(self, func, *args, **kwargs):
        return func(*args, **kwargs)


class TestSampleServicePb(BaseService):
    def __init__(self, ctx):
        super(TestSampleServicePb, self).__init__(ctx)

    def hello(self, bs: bytes):
        # add a delay
        # time.sleep(randint(50, 300) / 1000)
        obj = SampleServicePbRequest()
        obj.ParseFromString(bs)
        ret = SampleServicePbResult(result=obj.name).SerializeToString()
        counter.inc()
        return ret


def _run_server():
    listener = AioListener(('127.0.0.1', 12201), "test_app")
    print("starting")
    listener.run_threading()
    listener.handler.register_interface(interface, TestSampleServicePb)
    listener.handler.executor = CoroExecutor()
    asyncio.run_coroutine_threadsafe(counter.print_count(), loop=listener._loop)


####
# fork clients

def _call(name):
    client = AioClient("perftestapp")
    client.mesh_service_address = ("127.0.0.1", 12201)
    for i in range(100):
        try:
            ret = client.invoke_sync(interface, "hello",
                                     SampleServicePbRequest(name=str(name)).SerializeToString(),
                                     timeout_ms=1000, spanctx=SpanContext())
        except Exception as e:
            pass
    print("{} finished".format(name))


def _acall(name):
    client = AioClient("perftestapp")
    client.mesh_service_address = ("127.0.0.1", 12201)
    fs = [client.invoke_async(interface, "hello",
                              SampleServicePbRequest(name=str(name)).SerializeToString(),
                              timeout_ms=1000, spanctx=SpanContext()) for i in range(100)]
    wait(fs)


if __name__ == '__main__':
    _run_server()
    executor = ProcessPoolExecutor(max_workers=100)
    result = executor.map(_call, range(100), timeout=5)

    executor.shutdown(wait=False)

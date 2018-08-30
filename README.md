# anthuner(a.k.a. sofa-bolt-python)

anthunder是一个python3实现的BOLT协议库，提供BOLT client和server功能，支持使用BOLT + Protobuf方式的RPC调用。

## requirements

- python3 >= 3.4 (aio classes needs asyncio support)
- python2.7 (limited support, needs extra 3rd party libraries)


## roadmap

- [x] 支持Bolt+pb调用服务端（client端）
- [x] 支持通过servicemesh的服务发现与服务发布
- [x] 支持使用Bolt+pb提供服务（server端）
- [ ] 支持调用其它序列化方式(hessian/java)提供的服务接口

## Tutorial

### 做为调用方
0. 获取服务方提供的 `.proto` 文件
1. 执行`protoc --python_out=. *.proto`命令，编译protobuf文件获得`_pb2.py`文件
2. 导入pb类并调用接口

```python
from SampleServicePbResult_pb2 import SampleServicePbResult
from SampleServicePbRequest_pb2 import SampleServicePbRequest

from anthunder import AioClient


spanctx = ctx                   # ctx is transfered from upstream rpc, which is an object of mytracer.SpanContext, stores rpc_trace_context
# spanctx = SpanContext()       # or generate a new context
client = AioClient(my_app_name) # will create a thread, and send heartbeat to mesh every 30s

interface = 'com.alipay.rpc.common.service.facade.pb.SampleServicePb:1.0'

# 订阅服务
client.subscribe(interface)

# 同步调用
content = client.invoke_sync(interface, "hello",
                             SampleServicePbRequest(name=some_name).SerializeToString(),
                             timeout_ms=500, spanctx=spanctx)
result = SampleServicePbResult()
result.ParseFromString(content)

# 异步调用

def client_callback(resp):
    # callback function, accepts bytes as the only argument,
    # then do deserialize and further processes
    result = SampleServicePbResult()
    result.ParseFromString(content)
    # do something

future = client.invoke_async(interface, "hello", 
                             SampleServicePbRequest(name=some_name).SerializeToString(),
                             spanctx=spanctx, callback=client_callback)
)

```

参考unittest

### 做为服务方

```python
from anthunder.listener import aio_listener

class SampleService(object):
    def __init__(self, ctx):
        # service must accept one param as spanctx for rpc tracing support
        self.ctx = ctx
        
    def hello(self, bs: bytes):
        obj = SampleServicePbRequest()
        obj.ParseFromString(bs)
        print("Processing Request", obj)
        return SampleServicePbResult(result=obj.name).SerializeToString()


listener = aio_listener.AioListener(('127.0.0.1', 12200), "test_app")
# register interface and its function, plus its protobuf definition class
listener.handler.register_interface("com.alipay.rpc.common.service.facade.pb.SampleServicePb:1.0",
                                    SampleService)
# start server in a standalone thread
listener.run_threading()
# or start in current thread
listener.run_forever()

# publish interfaces to service mesh
listener.publish()

# shutdown the server
listener.shutdown()

```

## License

Copyright (c) 2018-present, Ant Financial Service Group

Apache License 2.0

See LICENSE file.

## Thirdparty

Part of the mysockpool package uses codes from (urllib3)[https://github.com/urllib3/urllib3] project 
under the term of MIT License. See origin-license.txt under the mysockpool package.


# anthunder(a.k.a. sofa-bolt-python)

[![License](https://img.shields.io/pypi/l/anthunder.svg)](https://pypi.org/project/anthunder/)
[![Version](https://img.shields.io/pypi/v/anthunder.svg)](https://pypi.org/project/anthunder/)
[![Wheel](https://img.shields.io/pypi/wheel/anthunder.svg)](https://pypi.org/project/anthunder/)
[![Python](https://img.shields.io/pypi/pyversions/anthunder.svg)](https://pypi.org/project/anthunder/)
[![devstatus](https://img.shields.io/pypi/status/anthunder.svg)](https://pypi.org/project/anthunder/)
[![Build Status](https://img.shields.io/travis/sofastack/sofa-bolt-python/master.svg)](https://travis-ci.org/sofastack/sofa-bolt-python)
[![Build Status](./actions/workflows/unittest.yml/badge.svg)](./actions)

[![codecov](https://img.shields.io/codecov/c/gh/sofastack/sofa-bolt-python/master.svg)](https://codecov.io/gh/sofastack/sofa-bolt-python)
[![codebeat](https://codebeat.co/badges/59c6418c-72a1-4229-b363-686a2640e9d5)](https://codebeat.co/projects/github-com-alipay-sofa-bolt-python-master)

See [English README](./blob/master/README.en.md)

anthunder是一个python实现的BOLT协议库，提供BOLT client和server功能，支持使用BOLT + Protobuf方式的RPC调用。

## requirements

- python3 >= 3.5 (aio classes needs asyncio support)
- mosn >= 1.3 (to use with version >= 0.6)
- mosn < 1.3 (to use with version < 0.6)

## roadmap

- [x] 支持Bolt+pb调用服务端（client端）
- [x] 支持通过servicemesh的服务发现与服务发布
- [x] 支持使用Bolt+pb提供服务（server端）
- [x] 支持其它序列化协议

## Tutorial
以下示例以使用protobuf序列化为例。其它序列化协议请参考demo。

### 做为调用方
0. 获取服务方提供的 `.proto` 文件
1. 执行`protoc --python_out=. *.proto`命令，编译protobuf文件获得`_pb2.py`文件
2. 导入pb类并调用接口

```python
from SampleServicePbResult_pb2 import SampleServicePbResult
from SampleServicePbRequest_pb2 import SampleServicePbRequest

from anthunder import AioClient
from anthunder.discovery.mosn import MosnClient, ApplicationInfo


spanctx = ctx                   # ctx is transfered from upstream rpc, which is an object of mytracer.SpanContext, stores rpc_trace_context
# spanctx = SpanContext()       # or generate a new context
service_reg = MosnClient()      # using mosn for service discovery, see https://mosn.io for detail
service_reg.startup(ApplicationInfo(YOUR_APP_NAME))
# service_reg = LocalRegistry({interface: (inf_ip, inf_port)})  # or a service-address dict as service discovery

# 订阅服务, subscribe before client's requests
service_reg.subscribe(interface)

client = AioClient(YOUR_APP_NAME, service_register=service_reg) # will create a thread, and send heartbeat to remote every 30s

interface = 'com.alipay.rpc.common.service.facade.pb.SampleServicePb:1.0'


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
from anthunder import AioListener
from anthunder.discovery.mosn import MosnClient, ApplicationInfo


class SampleService(object):
    def __init__(self, ctx):
        # service must accept one param as spanctx for rpc tracing support
        self.ctx = ctx
        
    def hello(self, bs: bytes):
        obj = SampleServicePbRequest()
        obj.ParseFromString(bs)
        print("Processing Request", obj)
        return SampleServicePbResult(result=obj.name).SerializeToString()


interface = 'com.alipay.rpc.common.service.facade.pb.SampleServicePb:1.0'

service_reg = MosnClient()      # using mosn for service discovery, see https://mosn.io for detail
service_reg.startup(ApplicationInfo(YOUR_APP_NAME))
listener = AioListener(('127.0.0.1', 12199), YOUR_APP_NAME, service_register=service_reg)
# register interface and its function, plus its protobuf definition class
listener.register_interface(interface, service_cls=SampleService, provider_meta=ProviderMetaInfo(appName="test_app"))
# start server in a standalone thread
listener.run_threading()
# or start in current thread
listener.run_forever()

# publish interfaces, MUST after listener start.
listener.publish()

# shutdown the server
listener.shutdown()

```

## License

Copyright (c) 2018-present, Ant Financial Service Group

Apache License 2.0

See LICENSE file.

## Thirdparty

Part of the mysockpool package uses codes from [urllib3](https://github.com/urllib3/urllib3) project 
under the term of MIT License. See origin-license.txt under the mysockpool package.


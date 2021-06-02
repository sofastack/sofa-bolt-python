# anthunder(a.k.a. sofa-bolt-python)

anthunder(ant thunder) is a sofa-bolt library written in python. 
It supports RPC calling via 'sofa-bolt + protobuf' protocol.

## requirements

- python3 >= 3.5 (aio classes needs asyncio support)
- python2.7 (limited support, needs extra 3rd party libraries)
- mosn >= 1.3 (to use with version >= 0.6)
- mosn < 1.3 (to use with version < 0.6)

## roadmap

- [x] bolt client(protobuf serialization)
- [x] service discover via mosn (sofa servicemesh sidecar)
- [x] bolt server(protobuf serialization)
- [ ] hessian2 serialization support

## Tutorial

### As client (caller)
0. Acquire `.proto` file
1. Execute `protoc --python_out=. *.proto` to compile protobuf file, and get `_pb2.py` file.
2. Import protobuf classes (postfixed with `_pb2`)

```python
from SampleServicePbResult_pb2 import SampleServicePbResult
from SampleServicePbRequest_pb2 import SampleServicePbRequest

from anthunder import AioClient
from anthunder.discovery.mosn import MosnClient, ApplicationInfo


spanctx = SpanContext()         # generate a new context, an object of mytracer.SpanContext, stores rpc_trace_context.
# spanctx = ctx                 # or transfered from upstream rpc
service_reg = MosnClient()      # using mosn for service discovery, see https://mosn.io for detail
service_reg.startup(ApplicationInfo(YOUR_APP_NAME))
# service_reg = LocalRegistry({interface: (inf_ip, inf_port)})  # or a service-address dict as service discovery

# Subscribe interface before client requests
service_reg.subscribe(interface)

client = AioClient(YOUR_APP_NAME, service_register=service_reg) 
# will create a thread, and send heartbeat to remote every 30s

interface = 'com.alipay.rpc.common.service.facade.pb.SampleServicePb:1.0'


# Call synchronously
content = client.invoke_sync(interface, "hello",
                             SampleServicePbRequest(name=some_name).SerializeToString(),
                             timeout_ms=500, spanctx=spanctx)
result = SampleServicePbResult()
result.ParseFromString(content)

# Call asynchronously

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

See project's unittest for runnable demo

### As server

```python
from anthunder.listener import aio_listener
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
listener = aio_listener.AioListener(('127.0.0.1', 12200), YOUR_APP_NAME, service_register=service_reg)
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


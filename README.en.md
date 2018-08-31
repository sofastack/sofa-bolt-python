# anthuner(a.k.a. sofa-bolt-python)

anthunder(ant thunder) is a sofa-bolt library written in python. 
It supports RPC calling via 'sofa-bolt + protobuf' protocol.

## requirements

- python3 >= 3.4 (aio classes needs asyncio support)
- python2.7 (limited support, needs extra 3rd party libraries)


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


spanctx = SpanContext()         # generate a new context, an object of mytracer.SpanContext, stores rpc_trace_context.
# spanctx = ctx                 # or transfered from upstream rpc
client = AioClient(my_app_name) # my_app_name will be send to sidecar as caller name.
                                # will create a thread, and send heartbeat to mesh every 30s

interface = 'com.alipay.rpc.common.service.facade.pb.SampleServicePb:1.0'

# Subscribe interface
client.subscribe(interface)

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


# automatically generated file, edit carefully!!
from anthunder import Client, Request, SERVICE_MAP


class SampleService(Request):

    def hello(self, **kwargs):
        from .SampleServicePbRequest_pb2 import SampleServicePbRequest as RequestMessage
        from .SampleServicePbResult_pb2 import SampleServicePbResult as ResultMessage

        req = RequestMessage(**kwargs).SerializeToString()
        resp = Client("anthunderTestAppName").invoke_sync("com.alipay.rpc.common.service.facade.pb.SampleServicePb:1.0",
                                                          "hello", req,
                                                          timeout_ms=500, target_app="bar1",
                                                          spanctx=self.spanctx)
        result = ResultMessage()
        result.ParseFromString(resp)
        return result

    def helloComplex(self, **kwargs):
        from .ComplexServicePbRequest_pb2 import ComplexServicePbRequest as RequestMessage
        from .ComplexServicePbResult_pb2 import ComplexServicePbResult as ResultMessage

        req = RequestMessage(**kwargs).SerializeToString()
        resp = Client("anthunderTestAppName").invoke_sync("com.alipay.rpc.common.service.facade.pb.SampleServicePb:1.0",
                                                          "helloComplex", req,
                                                          timeout_ms=500, target_app="bar1",
                                                          spanctx=self.spanctx)
        result = ResultMessage()
        result.ParseFromString(resp)
        return result


SERVICE_MAP["com.alipay.rpc.common.service.facade.pb.SampleServicePb:1.0"] = ("127.0.0.1", 12200)

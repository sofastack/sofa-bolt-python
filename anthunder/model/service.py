import attr


class BaseService(object):
    """
    Service classes provides service interfaces.
    After registering to a interface, Listener will create a object of Service type on each request on this interface, 
    and call to the method specified in request header with request body bytes.
    The object is created with a spanctx as its first positional argument, such spanctx can than be referenced 
    by self.ctx, and used in logging and/or passing to downstream in later rpc calling.
    """
    def __init__(self, ctx):
        self.ctx = ctx


@attr.s
class ProviderMetaInfo(object):
    appName = attr.ib()
    protocol = attr.ib(default="1")
    version = attr.ib(default="4.0")
    serializeType = attr.ib(default="protobuf")
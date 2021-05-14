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
    protocol = attr.ib()
    version = attr.ib()
    serializeType = attr.ib()
    appName = attr.ib()


class ServiceMeta(object):
    """
    Service metadata object
    """
    def __init__(self, name: str, provider_metadata: ProviderMetaInfo):
        self.name = name
        self.provider_metadata = provider_metadata

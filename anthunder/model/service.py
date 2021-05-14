import attr


@attr.s
class ProviderMetaInfo(object):
    protocol = attr.ib()
    version = attr.ib()
    serializeType = attr.ib()
    appName = attr.ib()


class Service(object):
    """
    Service metadata object
    """
    def __init__(self, name: str, provider_metadata: ProviderMetaInfo):
        self.name = name
        self.provider_metadata = provider_metadata

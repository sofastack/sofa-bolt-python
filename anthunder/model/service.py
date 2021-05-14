class Service(object):
    """
    Service metadata object
    """
    def __init__(self, name, provider_metadata):
        self.name = name
        self.provider_metadata = provider_metadata

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
   File Name : base_listener
   Author : jiaqi.hjq
"""
import attr
from urllib.parse import parse_qs


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
    appName = attr.ib(default="default")
    protocol = attr.ib(default="1")
    version = attr.ib(default="4.0")
    serializeType = attr.ib(default="protobuf")


class SubServiceMeta(object):
    """
    SubServiceMeta is metadata and addresses from service subscriber.
    In sofa stack with MOSN as data plane, this metadata is returned as a list of
    bolt url, with address as host:port, and metadata as querystring.
    """
    def __init__(self, address_list: list, metadata=None):
        self.addresses = [address_list] if isinstance(address_list,
                                                      str) else address_list
        self.metadata = metadata or ProviderMetaInfo()

    @classmethod
    def from_bolt_url(cls, url: str):
        # TODO: to support multiple addresses with weight sets in querystring
        # 127.0.0.1:12220?p=1&v=4.0&_SERIALIZETYPE=hessian2&app_name=someapp
        # 127.0.0.1:12220?p=1&v=4.0&_SERIALIZETYPE=protobuf&app_name=someapp
        addr, qs = url.split('?', 2)
        qsd = parse_qs(qs)
        pmi = ProviderMetaInfo(qsd.get('app_name', "default"),
                               qsd.get("protocol", "1"),
                               qsd.get("version", "4.0"),
                               qsd.get("_SERIALIZETYPE", "protobuf"))

        o = cls(addr, pmi)
        return o

    @property
    def address(self):
        # TODO: currently only returns the first address. 
        # should return different address round-robin or base on weight.
        return self.addresses[0]


PubServiceMeta = ProviderMetaInfo
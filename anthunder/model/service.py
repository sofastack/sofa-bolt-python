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
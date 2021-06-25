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
import logging
import threading

from anthunder.exceptions import ServerError

logger = logging.getLogger(__name__)


class BaseHandler(object):
    """Handle bolt request"""
    # stores interface:
    #   "interface": (function, protobuf_cls)
    interface_mapping = dict()

    def register_interface(self, interface, service_cls, *service_cls_args,
                           **service_cls_kwargs):
        raise NotImplementedError()

    def handle_request(self, ctx, service, method, body):
        raise NotImplementedError()


class BaseListener(object):
    """
    Base class for listener(server) implementation. provides publish/unpublish method.
    """
    handlerCls = BaseHandler

    def __init__(self,
                 address,
                 app_name,
                 *,
                 service_register=None,
                 **server_kwargs):
        """
        :param address: the socket address will be listened on.
        :type address: tuple (host:str, port:int)
        Check ApplicationInfo's comment for other params' explanations.
        """
        if isinstance(address, str):
            address = address.split(':', 2)
        self.address = address
        self.app_name = app_name
        self.server_kwargs = server_kwargs
        self.handler = self.handlerCls()
        self.service_register = service_register
        self.service_provider = dict()

    def initialize(self):
        raise NotImplementedError()

    def register_interface(self,
                           interface,
                           *,
                           provider_meta,
                           service_cls,
                           service_cls_args=None,
                           service_cls_kwargs=None):
        service_cls_args = service_cls_args or tuple()
        service_cls_kwargs = service_cls_kwargs or dict()
        self.handler.register_interface(interface, service_cls,
                                        *service_cls_args,
                                        **service_cls_kwargs)
        self.service_provider[interface] = provider_meta

    def publish(self):
        """
        Publish all the interfaces in handler.interface_mapping to mosnd
        """
        if self.service_register:
            for service_name, provider_meta in self.service_register:
                self.service_register.publish(self.address, service_name,
                                              provider_meta)

    def unpublish(self):
        """
        Revoke all the interfaces in handler.interface_mapping from mosnd.
        """
        if self.service_register:
            for service_name in self.service_register:
                self.service_register.unpublish(service_name)

    def run_forever(self):
        raise NotImplementedError()

    def shutdown(self):
        raise NotImplementedError()

    def run_threading(self):
        t = threading.Thread(target=self.run_forever, daemon=True)
        t.start()


class NoProcessorError(ServerError):
    pass

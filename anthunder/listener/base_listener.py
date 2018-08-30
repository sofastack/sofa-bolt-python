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

from anthunder.mesh.mesh_client import MeshClient, PublishServiceRequest, ProviderMetaInfo, ApplicationInfo

logger = logging.getLogger(__name__)


class BaseService(object):
    def __init__(self, ctx):
        self.ctx = ctx


class BaseHandler(object):
    """Handle bolt request"""
    # stores interface:
    #   "interface": (function, protobuf_cls)
    interface_mapping = dict()

    def register_interface(self, interface, service_cls):
        raise NotImplementedError()

    def handle_request(self, ctx, service, method, body):
        raise NotImplementedError()


class BaseListener(object):
    handlerCls = BaseHandler

    def __init__(self, address, app_name, data_center="", zone="", **server_kwargs):
        self.address = address
        self.app_name = app_name
        self.server_kwargs = server_kwargs
        self.handler = self.handlerCls()
        try:
            self._mesh_client = MeshClient(ApplicationInfo(app_name, data_center, zone))
            self._mesh_client.startup()
        except:
            logger.error("Fail to startup mesh client")
            self._mesh_client = None

    def initialize(self):
        raise NotImplementedError()

    def publish(self):
        if self._mesh_client:
            for service_name in self.handler.interface_mapping:
                self._mesh_client.publish(PublishServiceRequest(
                    serviceName=service_name,
                    providerMetaInfo=ProviderMetaInfo(protocol="1",
                                                      version="4.0",
                                                      serializeType="protobuf",
                                                      appName=self.app_name)))

    def unpublish(self):
        if self._mesh_client:
            for service_name in self.handler.interface_mapping:
                self._mesh_client.unpublish(service_name)

    def run_forever(self):
        raise NotImplementedError()

    def shutdown(self):
        raise NotImplementedError()

    def run_threading(self):
        t = threading.Thread(target=self.run_forever, daemon=True)
        t.start()

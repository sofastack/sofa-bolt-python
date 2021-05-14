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
   File Name : base.py
   Author : jiaqi.hjq
"""
import logging

from anthunder import SERVICE_MAP
from anthunder.discovery.mesh_client import MeshClient, ApplicationInfo

logger = logging.getLogger(__name__)


class _BaseClient(object):
    """
    Basic class for client implementation. Provides subscribe/unsubscribe method.
    """
    mesh_service_address = ("127.0.0.1", 12220)
    sofa_default_port = 12200

    def __init__(self, app_name, data_center=None, zone=None, registry_end_point=None,
                 is_antsharecloud=False, access_key=None, secret_key=None):
        """
        Check ApplicationInfo's comment for params' explanations.
        """
        try:
            self._mesh_client = MeshClient(ApplicationInfo(app_name, data_center, zone, registry_end_point,
                                                           access_key, secret_key, is_antsharecloud))
            self._mesh_client.startup()
            logger.info("Mesh client started!")
        except:
            logger.error("Fail to startup mesh client")
            self._mesh_client = None

    def _get_address(self, interface):
        addr = SERVICE_MAP.get(interface, self.mesh_service_address)
        if isinstance(addr, str):
            logger.debug("address is str({}), using default port({})".format(addr, self.sofa_default_port))
            addr = (addr, self.sofa_default_port)
        return addr

    def subscribe(self, *interface):
        """
        Subscribe interfaces from mosnd, must called one before call to relevant interface.
        :param interface: the interface name.
        :type interface: str
        """
        if not self._mesh_client:
            return
        for inf in interface:
            logger.info("Subscribe interface ({}) through mesh".format(inf))
            try:
                self._mesh_client.subscribe(inf)
                SERVICE_MAP[inf] = self.mesh_service_address
            except Exception as e:
                logger.error(e)

    def unsubscribe(self, *interface):
        """
        Unsubscribe interfaces from mosnd.

        :param interface: the interface name
        :type interface: str
        """
        if not self._mesh_client:
            return
        for inf in interface:
            logger.info("Unsubscribe interface ({}) through mesh".format(inf))
            try:
                self._mesh_client.unsubscribe(inf)
                SERVICE_MAP.pop(inf)
            except Exception as e:
                logger.error(e)

    def invoke_sync(self, interface, method, content, **kwargs):
        raise NotImplementedError()

    def invoke_async(self, interface, method, content, **kwargs):
        raise NotImplementedError()

    def invoke_oneway(self, interface, method, content, **kwargs):
        raise NotImplementedError()

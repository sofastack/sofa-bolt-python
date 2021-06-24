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
   File Name : __init__.py
   Author : jiaqi.hjq
"""
import logging

logger = logging.getLogger(__name__)
from anthunder.helpers.singleton import Singleton
from anthunder.helpers.immutable_dict import ImmutableValueDict
from anthunder.model.service import SubServiceMeta, ProviderMetaInfo


class LocalRegistry(object):
    """
    A simple service registry with all addresses hardcode in object of this class.
    For test purpose only.
    Any service running in production should be in service mesh or use a service discovery
    services to obtain remote addresses.
    """
    __metaclass__ = Singleton

    keep_alive = False  # only for mesh heartbeat

    def __init__(self, servicemap):
        self._service_meta_map = ImmutableValueDict(servicemap)

    def subscribe(self, service):
        logger.warning("local registry does not support this method")

    def unsubscribe(self, service):
        logger.warning("local registry does not support this method")

    def publish(self, service):
        logger.warning("local registry does not support this method")

    def unpublish(self, service):
        logger.warning("local registry does not support this method")

    def get_address(self, interface: str) -> str:
        """
        :return: address str
        """
        meta = self._service_meta_map.get(interface)
        if meta is None:
            raise Exception(
                "No address available for {}, you meed to declare it explicitly in LocalRegistry's init parameter"
                .format(interface))
        return meta.address[0]

    def get_metadata(self, interface: str) -> ProviderMetaInfo:
        meta = self._service_meta_map.get(interface)
        if meta is None:
            raise Exception(
                "No available interface for {}, you meed to declare it explicitly in LocalRegistry's init parameter"
                .format(interface))
        return meta.metadata


class FixedAddressRegistry(LocalRegistry):
    """always returns fixed address, for test purpose only."""
    def __init__(self, address, metadata: ProviderMetaInfo = None):
        self._address = address
        self._metadata = metadata or ProviderMetaInfo()

    def get_address(self, service) -> str:
        return self._address

    def get_metadata(self, service: str) -> ProviderMetaInfo:
        return self._metadata
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
        self._service_addr_map = ImmutableValueDict(servicemap)

    def subscribe(self, service):
        logger.warning("local registry does not support this method")

    def unsubscribe(self, service):
        logger.warning("local registry does not support this method")

    def publish(self, service):
        logger.warning("local registry does not support this method")

    def unpublish(self, service):
        logger.warning("local registry does not support this method")

    def get_address(self, service: str):
        return self._service_addr_map.get(service)


class FixedAddressRegistry(LocalRegistry):
    """always returns fixed address, for test purpose only."""
    def __init__(self, address):
        self._address = address

    def get_address(self, service):
        return self._address


LocalhostRegistry = FixedAddressRegistry(("127.0.0.1", 12200))
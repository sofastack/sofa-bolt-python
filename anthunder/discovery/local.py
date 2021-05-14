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
    A simple service registry with all addresses predefined
    """
    __metaclass__ = Singleton

    keep_alive = False  # only for mesh heartbeat

    def __init__(self, servicemap):
        self._serviceMap = ImmutableValueDict(servicemap)

    def subscribe(self, service):
        logger.warning("local registry does not support this method")

    def unsubscribe(self, service):
        logger.warning("local registry does not support this method")

    def publish(self, service):
        logger.warning("local registry does not support this method")

    def unpublish(self, service):
        logger.warning("local registry does not support this method")

    def get_address(self, interface):
        return self._serviceMap.get(interface)

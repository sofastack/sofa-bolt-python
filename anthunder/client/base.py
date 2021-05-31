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

logger = logging.getLogger(__name__)


class _BaseClient(object):
    """
    Basic class for client implementation. Provides subscribe/unsubscribe method.
    """
    def __init__(self, app_name, *, service_register=None):
        """
        Check ApplicationInfo's comment for params' explanations.
        """
        self._service_register = service_register

    def _get_address(self, interface):
        return self._service_register.get_address(interface)

    def invoke_sync(self, interface, method, content, **kwargs):
        raise NotImplementedError()

    def invoke_async(self, interface, method, content, **kwargs):
        raise NotImplementedError()

    def invoke_oneway(self, interface, method, content, **kwargs):
        raise NotImplementedError()

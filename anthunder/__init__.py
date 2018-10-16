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
   File Name : __init__
   Author : jiaqi.hjq
   Create Time : 2018/4/28 11:36
   Description : description what the main function of this file
   Change Activity:
        version0 : 2018/4/28 11:36 by jiaqi.hjq  init
"""

__all__ = ['Client', 'SockListener', 'BaseService', 'Request', 'SERVICE_MAP']

from anthunder.helpers.immutable_dict import ImmutableValueDict

SERVICE_MAP = ImmutableValueDict()

from anthunder.client.client import Client
from anthunder.listener.sock_listener import SockListener
from anthunder.listener.base_listener import BaseService
from anthunder.request import Request
import six

if six.PY34:
    __all__.extend(['AioListener', 'AioClient'])

    from anthunder.listener.aio_listener import AioListener
    from anthunder.client.aio_client import AioClient

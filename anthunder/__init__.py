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

    Bootstrap scripts:
    1. read config
    2. publish services
    3. subscribe services

   The services is written in a appointed json configfile by the syntax of below:
   {
        'publish': [
            'com.alipay.pub.service1': "protobuf class1 path",
            'com.alipay.pub.service2': "protobuf class2 path"
        ],
        'subscribe': [
            'com.alipay.sub.service1': "protobuf class3 path",
            'com.alipay.sub.service2': "protobuf class4 path"
        ]
   }
"""

__all__ = ['Client', 'AioClient', 'AioListener', 'BaseService', 'Request', 'SERVICE_MAP']

from anthunder.helpers.immutable_dict import ImmutableValueDict

SERVICE_MAP = ImmutableValueDict()

from anthunder.client import Client, AioClient
from anthunder.listener import AioListener, BaseService
from anthunder.request import Request

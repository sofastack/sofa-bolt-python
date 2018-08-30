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
   File Name : exceptions
   Author : jiaqi.hjq
   Create Time : 2018/4/28 14:13
   Description : description what the main function of this file
   Change Activity:
        version0 : 2018/4/28 14:13 by jiaqi.hjq  init
"""


class PyboltError(Exception):
    pass


class ServerError(PyboltError):
    def __init__(self, msg):
        super(ServerError, self).__init__("ServerError: {}".format(msg))

    @classmethod
    def from_statuscode(cls, code):
        return cls("ServerError: RESPSTATUS={0.value}, {0.name}".format(code))


class ClientError(PyboltError):
    def __init__(self, msg):
        super(ClientError, self).__init__("ClientError: {}".format(msg))

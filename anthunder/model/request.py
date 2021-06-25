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
   File Name : request
   Author : jiaqi.hjq
   Create Time : 2018/5/21 16:38
   Description : describe the main function of this file
   Change Activity:
        version0 : 2018/5/21 16:38 by jiaqi.hjq  init
"""


class Request(object):
    """
    Basic class for request object

    currently holds the rpc_trace_context attributes
    """

    def __init__(self, spanctx):
        self.spanctx = spanctx

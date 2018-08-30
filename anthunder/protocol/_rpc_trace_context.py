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
   File Name : rpc_trace_context
   Author : jiaqi.hjq
   Create Time : 2018/5/18 15:45
   Description : describe the main function of this file
   Change Activity:
        version0 : 2018/5/18 15:45 by jiaqi.hjq  init
"""


class RpcTraceContext(object):
    """
    Holds rpc_trace_context.xxx contexts, can be expanded for adding them to sofa_headers
    """
    prefix = "rpc_trace_context."

    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)

    def expand(self):
        return {self.prefix + k: str(v) for k, v in self.__dict__.items()}

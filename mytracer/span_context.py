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
   File Name : span_context
   Author : jiaqi.hjq
   Create Time : 2018/5/28 15:33
   Description : describe the main function of this file
   Change Activity:
        version0 : 2018/5/28 15:33 by jiaqi.hjq  init
"""
from ._rpc_id import RpcId
from ._trace_id import TraceId


class _ImmutableDict(dict):
    def __setitem__(self, key, value):
        raise TypeError("This dict is not allowed to modify")


class SpanContext(object):
    """
    A mapping holding the span related context.

    currently:

    sofaRpcId='0',
    sofaTraceId='0123456789abcdef0123456789abcd',

    """

    def __init__(self, reference=None, **kwargs):
        """
        :param reference: contains a type and a context
        :param kwargs:
        """
        if reference:
            origin_span_baggage = reference.referenced_context.baggage.copy()
            kwargs['sofaRpcId'] = origin_span_baggage.pop('sofaRpcId').new_by_reference_type(reference.type)
            kwargs.update(origin_span_baggage)
        else:
            kwargs['sofaTraceId'] = TraceId(kwargs.pop('sofaTraceId', None))
            _ids = list(kwargs.pop('sofaRpcId', '1').split('.'))
            kwargs['sofaRpcId'] = RpcId(*_ids)
        self._baggage = _ImmutableDict(**kwargs)

    @property
    def baggage(self):
        return self._baggage

    def __str__(self):
        return str(self.baggage)

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
   Create Time : 2018/5/25 16:27
   Description : describe the main function of this file
   Change Activity:
        version0 : 2018/5/25 16:27 by jiaqi.hjq  init

### Workflow for client side tracing:

 - Prepare request
 - Load the current trace state
 - Start a span
 - Inject the span into the request
 - Send request
 - Receive response
 - Finish the span

### The workflow for tracing a server request is as follows:

 - Server Receives Request
 - Extract the current trace state from the inter-process transport (HTTP, etc)
 - Start the span
 - Store the current trace state
 - Server Finishes Processing the Request / Sends Response
 - Finish the span

"""

__all__ = [
    "MyTracer",
    "MySpan",
    "SpanContext",
    "new_span",
    "child_span_of",
    "follows_span_from",
    "RpcId",
    "TraceId",
    "tracer"
]

from .tracer import MyTracer
from .span import MySpan
from .span_context import SpanContext
from .helpers import new_span, child_span_of, follows_span_from, tracer
from ._rpc_id import RpcId
from ._trace_id import TraceId

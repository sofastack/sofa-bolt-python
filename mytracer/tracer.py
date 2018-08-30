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
   File Name : mytracer
   Author : jiaqi.hjq
   Create Time : 2018/5/25 16:30
   Description : describe the main function of this file
   Change Activity:
        version0 : 2018/5/25 16:30 by jiaqi.hjq  init
"""
import six
import threading

import opentracing

from .span import MySpan
from .span_context import SpanContext


class MyTracer(opentracing.Tracer):
    """
    Tracer is the entry point API between instrumentation code and the
    tracing implementation.

    Should be statless
    """
    spanCls = MySpan
    spanContextCls = SpanContext
    _local = threading.local()
    _prefix = 'rpc_trace_context.'

    def start_span(self, operation_name, child_of=None, references=None, tags=None, start_time=None):
        """Starts and returns a new Span representing a unit of work.


        Starting a root Span (a Span with no causal references)::

            tracer.start_span('...')


        Starting a child Span (see also start_child_span())::

            tracer.start_span(
                '...',
                child_of=parent_span)


        Starting a child Span in a more verbose way::

            tracer.start_span(
                '...',
                references=[opentracing.child_of(parent_span)])


        :param operation_name: name of the operation represented by the new
            span from the perspective of the current service.
        :param child_of: (optional) a Span or SpanContext instance representing
            the parent in a REFERENCE_CHILD_OF Reference. If specified, the
            `references` parameter must be omitted.
        :param references: (optional) a list of Reference objects that identify
            one or more parent SpanContexts. (See the Reference documentation
            for detail)
        :param tags: an optional dictionary of Span Tags. The caller gives up
            ownership of that dictionary, because the Tracer may use it as-is
            to avoid extra data copying.
        :param start_time: an explicit Span start time as a unix timestamp per
            time.time()

        :return: Returns an already-started Span instance.
        """
        if isinstance(child_of, SpanContext):
            ref = opentracing.child_of(child_of)
        elif isinstance(child_of, MySpan):
            ref = opentracing.child_of(child_of.context)
        elif references:
            ref = references if isinstance(references, opentracing.Reference) else references[0]
        else:
            ref = None

        span = self.spanCls(tracer=self,
                            context=self.spanContextCls(ref))

        span.set_operation_name(operation_name)

        _tags = tags or dict()
        for k, v in _tags:
            span.set_tag(k, v)
        if start_time:
            span.set_start_time(start_time)

        return span

    def extract(self, format, carrier):
        """
        return a span context
        :param format:
        :param carrier: dict: currently support:
            SofaHeader(dict)
        :return:
        """
        if format != opentracing.Format.TEXT_MAP:
            raise opentracing.UnsupportedFormatException()
        try:
            d = {k.split('.', 1)[1]: carrier[k] for k in carrier if k.startswith(self._prefix)}
            return self.spanContextCls(None, **d)
        except:
            raise opentracing.InvalidCarrierException()

    def inject(self, span_context, format, carrier):
        """
        inject span context into a carrier
        :param span_context:
        :param format:
        :param carrier:
        :return:
        """
        if format != opentracing.Format.TEXT_MAP:
            raise opentracing.UnsupportedFormatException()

        for k, v in span_context.baggage.items():
            carrier[self._prefix + k] = str(v)
        return carrier

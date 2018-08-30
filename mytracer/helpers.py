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
   File Name : helpers
   Author : jiaqi.hjq
"""
from opentracing import Reference, ReferenceType

from mytracer.tracer import MyTracer

tracer = MyTracer()


def new_span(operation_name, **tags):
    return tracer.start_span(operation_name, tags=tags)


def child_span_of(span, operation_name=None, **tags):
    operation_name = operation_name or span.operation_name
    return tracer.start_span(operation_name, child_of=span, tags=tags)


def follows_span_from(span, operation_name=None, **tags):
    operation_name = operation_name or span.operation_name
    ref = Reference(ReferenceType.FOLLOWS_FROM, span.context)
    return tracer.start_span(operation_name, references=ref, tags=tags)

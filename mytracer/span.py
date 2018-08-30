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
   File Name : span
   Author : jiaqi.hjq
   Create Time : 2018/5/28 15:34
   Description : describe the main function of this file
   Change Activity:
        version0 : 2018/5/28 15:34 by jiaqi.hjq  init
"""
import time


class MySpan(object):
    def __init__(self, tracer, context):
        self._tracer = tracer
        self._context = context
        self._tags = dict()
        self._logs = dict()
        self._start_time = time.time()
        self._finish_time = None
        self._operation_name = ""

    @property
    def context(self):
        return self._context

    @property
    def operation_name(self):
        return self._operation_name

    def set_operation_name(self, operation_name):
        self._operation_name = operation_name

    def set_baggage_item(self, key, value):
        self._context._baggage[key] = value

    def get_baggage_iterm(self, key):
        return self._context.baggage[key]

    def set_tag(self, key, value):
        self._tags[key] = value

    def set_start_time(self, starttime):
        self._start_time = starttime

    def finish(self):
        self._finish_time = time.time()

    def __enter__(self):
        self._start_time = time.time()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.finish()

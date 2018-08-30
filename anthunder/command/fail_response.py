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
   File Name : fail_response.py
   Author : jiaqi.hjq
"""
import logging

from anthunder.protocol import BoltResponse
from anthunder.protocol._sofa_header import empty_header
from anthunder.protocol.constants import PTYPE, CMDCODE

logger = logging.getLogger(__name__)


class FailResponse(BoltResponse):
    @classmethod
    def response_to(cls, request_id, status_code):
        return cls(empty_header, b'', respstatus=status_code,
                   ptype=PTYPE.RESPONSE, cmdcode=CMDCODE.RESPONSE, request_id=request_id)

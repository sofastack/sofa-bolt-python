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
   File Name : test_helpers
   Author : jiaqi.hjq
"""
import logging
import unittest

from anthunder.helpers.immutable_dict import ImmutableValueDict
from anthunder.helpers.request_id import RequestId

logger = logging.getLogger(__name__)


class TestHelpers(unittest.TestCase):
    def test_request_id(self):
        rid = next(RequestId)
        print(rid)
        self.assertTrue(0 <= rid <= 0x7fffffff)

    def test_immutabledict(self):
        d = ImmutableValueDict()
        d['a'] = 'b'
        self.assertEqual(d['a'], 'b')
        with self.assertRaises(KeyError):
            d['a'] = 'a'
        self.assertEqual(d['a'], 'b')
        d['b'] = 'a'
        self.assertEqual(d['b'], 'a')


if __name__ == '__main__':
    unittest.main()

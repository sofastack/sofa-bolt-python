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
   File Name : _span_id
   Author : jiaqi.hjq
   Create Time : 2018/5/28 14:59
   Description : describe the main function of this file
   Change Activity:
        version0 : 2018/5/28 14:59 by jiaqi.hjq  init
"""


class RpcId(object):
    def __init__(self, *rpcids):
        """
        span id, represented as `a.b.c...`, where `a`, `b`, `c` are numbers.

        :param rpcids: numbers
        :type rpcids: int or str, last one must be int.
        """
        if not rpcids:
            self.rpcids = [1]
        else:
            def _innertrans(s):
                try:
                    return int(s)
                except ValueError:
                    return s

            self.rpcids = list(map(_innertrans, rpcids))
            if not isinstance(self.rpcids[-1], int):
                raise TypeError("Illigal span id, last segment must be int, not '{}'.".format(self.rpcids[-1]))

        self._child_count = 0
        self._parent = None

    def __str__(self):
        return ".".join(map(str, self.rpcids))

    __repr__ = __str__

    @classmethod
    def extend_id(cls, ids, extend):
        """extend a existing ids to a new one"""
        new_ids = list(ids)
        new_ids.append(extend)
        return cls(*new_ids)

    def _new_child_of(self):
        self._child_count += 1
        obj = self.extend_id(self.rpcids, self._child_count)
        obj._parent = self  # attach a link to parent rpcId
        return obj

    def _new_follows_from(self):
        obj = self.extend_id(self.rpcids[:-1], self.rpcids[-1] + 1)
        if self._parent:
            # a follows up span is a sibling span, means it is a child span of parent
            self._parent._child_count += 1
            obj._parent = self._parent
        return obj

    def new_by_reference_type(self, ref_type):
        return getattr(self, '_new_' + ref_type)()

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        if len(self.rpcids) != len(other.rpcids):
            return False
        return all(map(lambda x: x[0] == x[1], zip(self.rpcids, other.rpcids)))

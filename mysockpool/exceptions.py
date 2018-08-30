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

    Original Copyright 2008-2016 Andrey Petrov and contributors
    (see https://github.com/urllib3/urllib3/blob/master/CONTRIBUTORS.txt)
    under the MIT license (https://opensource.org/licenses/MIT).
   ------------------------------------------------------
   File Name : exceptions
"""


class MysockpoolError(Exception):
    "Base exception for errors caused within a pool."

    def __init__(self, pool, message):
        self.pool = pool
        super(MysockpoolError, self).__init__(self, "%s: %s" % (pool, message))

    def __reduce__(self):
        # For pickling purposes.
        return self.__class__, (None, None)


class EmptyPoolError(MysockpoolError):
    "Raised when a pool runs out of connections and no more are allowed."
    pass


class ClosedPoolError(MysockpoolError):
    "Raised when a request enters a pool after the pool has been closed."
    pass


class LocationValueError(ValueError, MysockpoolError):
    "Raised when there is something wrong with a given URL input."
    pass

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
   File Name : _wait
"""
try:
    from selectors import DefaultSelector, EVENT_READ, EVENT_WRITE
except ImportError:
    # python2.7
    from selectors34 import DefaultSelector, EVENT_READ, EVENT_WRITE


def _wait_for_io_events(socks, events, timeout):
    """ Waits for IO events to be available from a list of sockets
    or optionally a single socket if passed in. Returns a list of
    sockets that can be interacted with immediately. """
    if not isinstance(socks, list):
        # Probably just a single socket.
        if hasattr(socks, "fileno"):
            socks = [socks]
        # Otherwise it might be a non-list iterable.
        else:
            socks = list(socks)
    with DefaultSelector() as selector:
        for sock in socks:
            selector.register(sock, events)
        return [key[0].fileobj for key in
                selector.select(timeout) if key[1] & events]


def wait_for_read(socks, timeout=None):
    """ Waits for reading to be available from a list of sockets
    or optionally a single socket if passed in. Returns a list of
    sockets that can be read from immediately. """
    return _wait_for_io_events(socks, EVENT_READ, timeout)


def wait_for_write(socks, timeout=None):
    """ Waits for writing to be available from a list of sockets
    or optionally a single socket if passed in. Returns a list of
    sockets that can be written to immediately. """
    return _wait_for_io_events(socks, EVENT_WRITE, timeout)

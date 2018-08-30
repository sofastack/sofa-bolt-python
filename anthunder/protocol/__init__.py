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
   Create Time : 2018/4/28 13:19
   Description : description what the main function of this file
   Change Activity:
        version0 : 2018/4/28 13:19 by jiaqi.hjq  init
"""
__all__ = ["BoltRequest", "BoltResponse", "SofaHeader", "RpcTraceContext"]

from ._request_pkg import BoltRequest
from ._response_pkg import BoltResponse
from ._sofa_header import SofaHeader
from ._rpc_trace_context import RpcTraceContext
# *
#  Request command protocol for v1
#  0     1     2           4           6           8          10           12          14         16
#  +-----+-----+-----+-----+-----+-----+-----+-----+-----+-----+-----+-----+-----+-----+-----+-----+
#  |proto| type| cmdcode   |ver2 |   requestId           |codec|        timeout        |  classLen |
#  +-----------+-----------+-----------+-----------+-----------+-----------+-----------+-----------+
#  |headerLen  | contentLen            |                             ... ...                       |
#  +-----------+-----------+-----------+                                                                                               +
#  |               className + header  + content  bytes                                            |
#  +                                                                                               +
#  |                               ... ...                                                         |
#  +-----------------------------------------------------------------------------------------------+
#
#  proto: code for protocol 目前这个值是1,表示 bolt
#  type: request(1)/response(0)/request oneway(2)
#  cmdcode: code for remoting command 心跳是0,request 是1, response 是2
#  ver2:version for remoting command 目前是1,以后可能扩展
#  requestId: id of request 请求的 requestId,响应时会带上
#  codec: code for codec 序列化,hessian 是1,pb 是11,java 是2
#  timeout: timeout for request 默认-1,本地调用的超时时间,这个是给服务端用来实现 failfast,单位毫秒
#  headerLen: length of header headerMap 的字节数
#  contentLen: length of content content 的字节数.
#
#  Response command protocol for v1
#  0     1     2     3     4           6           8          10           12          14         16
#  +-----+-----+-----+-----+-----+-----+-----+-----+-----+-----+-----+-----+-----+-----+-----+-----+
#  |proto| type| cmdcode   |ver2 |   requestId           |codec|respstatus |  classLen |headerLen  |
#  +-----------+-----------+-----------+-----------+-----------+-----------+-----------+-----------+
#  | contentLen            |                  ... ...                                              |
#  +-----------------------+                                                                       +
#  |                         className + header  + content  bytes                                  |
#  +                                                                                               +
#  |                               ... ...                                                         |
#  +-----------------------------------------------------------------------------------------------+
#  respstatus: response status 服务端响应结果状态
#
#
# 其他
# className固定,对于请求是com.alipay.sofa.rpc.core.request.SofaRequest
# 对于响应是com.alipay.sofa.rpc.core.response.SofaResponse

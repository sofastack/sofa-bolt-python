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
   File Name : startup
   Author : jiaqi.hjq
"""
from threading import RLock

import attr
import requests
from requests import ConnectionError

from anthunder.helpers.singleton import Singleton


@attr.s
class PublishServiceRequest(object):
    serviceName = attr.ib()
    providerMetaInfo = attr.ib()
    port = attr.ib()
    protocolType = attr.ib(default="DEFAULT")
    onlyPublishInCloud = attr.ib(default=False)


@attr.s
class ProviderMetaInfo(object):
    protocol = attr.ib()
    version = attr.ib()
    serializeType = attr.ib()
    appName = attr.ib()


@attr.s
class ApplicationInfo(object):
    """
    ApplicationInfo is the request sent to mosnd to register your application.
    For compatibility reasons, the param with False value (None, empty str, False, etc..) will be dropped
    when posting to monsd.

    :param: appName: your application's name
    :param: dataCenter: (optional) the datacenter where the application deployed.
    :param: zone: (optional) the zone where the application deployed.
    :param: registryEndPoint: (optional) the configcenter's endpoint address you want to register to.
    :param: antShareCloud: (optional) is your application deployed at Ant Cloud.
    :param: accessKey: (must when antShareCloud=True) your access key.
    :param: secretKey: (must when antShareCloud=True) your secrect key.
    """
    appName = attr.ib()
    dataCenter = attr.ib(default="")
    zone = attr.ib(default="")
    registryEndPoint = attr.ib(default="")
    accessKey = attr.ib(default="")
    secretKey = attr.ib(default="")
    antShareCloud = attr.ib(default=False)


class MeshClient(object):
    __metaclass__ = Singleton
    _server = "http://127.0.0.1:13330/{}".format

    def __init__(self, appinfo):
        """
        :param appinfo: application infomation data, see ApplicationInfo's comments.
        :type appinfo: ApplicationInfo, see ApplicationInfo's comments.
        """
        self.appinfo = appinfo
        self._sess = requests.session()
        self._rlock = RLock()
        self._started = False

    def startup(self):
        with self._rlock:
            if not self._started:
                self._post("configs/application", attr.asdict(self.appinfo, filter=lambda a, v: v))
                self._started = True
            return self._started

    def subscribe(self, service_str):
        return self._post("services/subscribe", dict(serviceName=service_str))

    def unsubscribe(self, service_str):
        return self._post("services/unsubscribe", dict(serviceName=service_str))

    def publish(self, publish_service_request):
        """
        :param publish_service_request:
        :type publish_service_request: PublishServiceRequest
        :return:
        """
        return self._post("services/publish", attr.asdict(publish_service_request))

    def unpublish(self, service_str):
        return self._post("services/unpublish", dict(serviceName=service_str))

    def _post(self, endpoint, json):
        addr = self._server(endpoint)
        r = self._sess.post(addr, json=json)
        if r.status_code != 200:
            raise ConnectionError("Connect to service mesh failed: {}".format(r.status_code))
        result = r.json()
        if result.get('success') is not True:
            raise ConnectionError("Connect to service mesh failed: {}".format(result.get('errorMessage',
                                                                                         "MISSING ERROR MESSAGE")))
        return result

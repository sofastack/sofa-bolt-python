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
   File Name : test_mesh_client
   Author : jiaqi.hjq
"""
import json
import unittest
import attr
import requests_mock

from anthunder.discovery.mosn import MosnClient, ApplicationInfo
from anthunder.model.service import ProviderMetaInfo


class TestMeshClient(unittest.TestCase):
    interface = "com.alipay.pybolt.test:1.0"
    provider = ProviderMetaInfo(protocol="1",
                                version="4.0",
                                serializeType="protobuf",
                                appName="pybolt_test_app")
    subinterface = "com.alipay.pybolt.subtest:1.0"
    appmeta = ApplicationInfo("pybolt_test_app", "", "", "")

    @requests_mock.Mocker()
    def test_start(self, session_mock):
        session_mock.post('http://127.0.0.1:13330/configs/application',
                          text=json.dumps(dict(success=True)))
        mesh = MosnClient()
        mesh.startup(self.appmeta)

    @requests_mock.Mocker()
    def test_pub(self, session_mock):
        session_mock.post('http://127.0.0.1:13330/configs/application',
                          text=json.dumps(dict(success=True)))
        session_mock.post('http://127.0.0.1:13330/services/publish',
                          text=json.dumps(dict(success=True)))
        print(attr.asdict(self.provider))
        mesh = MosnClient()
        mesh.startup(self.appmeta)
        mesh.publish(("127.0.0.1", 12200),
                     self.interface,
                     provider=self.provider)

    @requests_mock.Mocker()
    def test_subscribe(self, session_mock):
        session_mock.post('http://127.0.0.1:13330/configs/application',
                          text=json.dumps(dict(success=True)))
        session_mock.post('http://127.0.0.1:13330/services/subscribe',
                          text=json.dumps(dict(success=True)))
        mesh = MosnClient()
        mesh.startup(self.appmeta)
        mesh.subscribe(self.subinterface)

    @requests_mock.Mocker()
    def test_unpublish(self, session_mock):
        session_mock.post('http://127.0.0.1:13330/configs/application',
                          text=json.dumps(dict(success=True)))
        session_mock.post('http://127.0.0.1:13330/services/unpublish',
                          text=json.dumps(dict(success=True)))
        mesh = MosnClient()
        mesh.startup(self.appmeta)
        mesh.unpublish(self.interface)

    @requests_mock.Mocker()
    def test_unsubscribe(self, session_mock):
        print(session_mock)
        session_mock.post('http://127.0.0.1:13330/configs/application',
                          text=json.dumps(dict(success=True)))
        session_mock.post('http://127.0.0.1:13330/services/unsubscribe',
                          text=json.dumps(dict(success=True)))
        mesh = MosnClient()
        mesh.startup(self.appmeta)
        mesh.unsubscribe(self.subinterface)


if __name__ == '__main__':
    unittest.main()

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
   File Name : setup.py
   Author : jiaqi.hjq
   Create Time : 2018/4/28 11:36
   Description : description what the main function of this file
   Change Activity:
        version0 : 2018/4/28 11:36 by jiaqi.hjq  init
"""
import sys
from setuptools import setup, find_packages

install_requires = [
    "opentracing==1.3.0",
    "requests>=2.13.0",
    "attrs>=18.1.0",
    "six",
]
tests_requires=[
    "requests-mock>=1.5.0",
],
if sys.version_info <= (3, 3):
    install_requires.extend([
        'selectors34',
        'enum34',
        'ipaddress',
    ])
    tests_requires.extend([
        'mock',
    ])

with open('README.en.md', 'r', encoding='utf-8') as f:
    readme = f.read()
with open('HISTORY.md', 'r', encoding='utf-8') as f:
    history = f.read()

setup(
    name='anthunder',
    version='0.6.1',
    author='wanderxjtu',
    author_email='wanderhuang@gmail.com',
    url='https://github.com/alipay/sofa-bolt-python',
    packages=find_packages(exclude=["tests.*", "tests"]),
    license="Apache License 2.0",
    install_requires=install_requires,
    include_package_data=True,
    test_suite="tests",
    tests_requires=tests_requires,
    description="an(t)thunder is a sofa-bolt protocol lib.",
    long_description=readme + '\n\n' + history,
    long_description_content_type="text/markdown",
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy'
    ],
)

#!/usr/bin/env python
from setuptools import setup

py_files=[
    "ansible/module_utils/zabbix",
]
files = [
    "ansible/modules/zabbix",
]

long_description = open('README.md', 'r').read()

setup(
    name='ansible-modules-zabbix',
    version='0.1',
    description='Zabbix Ansible Modules',
    long_description=long_description,
    url='https://github.com/petercb/ansible-modules-zabbix',
    author='Peter Burns',
    author_email='pcburns@outlook.com',
    license='MIT',
    py_modules=py_files,
    packages=files,
    install_requires = [
        'ansible>=2.0.0',
        'zabbix-api>=0.4',
    ],
)

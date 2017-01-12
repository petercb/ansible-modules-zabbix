#!/usr/bin/env python
from setuptools import setup

py_files=[
    "ansible/module_utils/zabbix",
]
files = [
    "ansible/modules/zabbix",
]

setup(
    name='ansible-modules-zabbix',
    description='Zabbix Ansible Modules',
    use_scm_version=True,
    url='https://github.com/petercb/ansible-modules-zabbix',
    author='Peter Burns',
    author_email='pcburns@outlook.com',
    license='MIT',
    setup_requires=['setuptools_scm'],
    py_modules=py_files,
    packages=files,
    install_requires = [
        'ansible>=2.0.0',
        'zabbix-api>=0.4',
    ],
)

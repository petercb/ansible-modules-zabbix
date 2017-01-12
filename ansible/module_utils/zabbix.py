# -*- coding:utf8 -*-
"""Ansible module utility classes for Zabbix
"""

try:
    from zabbix_api import ZabbixAPI
    HAS_ZABBIX_API = True
except ImportError:
    HAS_ZABBIX_API = False

def zbx_argument_spec():
    return dict(
        server_url=dict(type='str', required=True, aliases=['url']),
        login_user=dict(type='str', required=True),
        login_password=dict(type='str', required=True, no_log=True),
        http_login_user=dict(type='str', required=False, default=None),
        http_login_password=dict(type='str', required=False, default=None, no_log=True),
        timeout=dict(type='int', default=10),
    )

class AnsibleZabbix(object):

    def __init__(self, module):
        if not HAS_ZABBIX_API:
            module.fail_json(msg="python library zabbix-api required: pip install zabbix-api")

        self._module = module
        self._connect()

    def _connect(self):
        server_url = self._module.params['server_url']
        login_user = self._module.params['login_user']
        login_password = self._module.params['login_password']
        http_login_user = self._module.params['http_login_user']
        http_login_password = self._module.params['http_login_password']
        timeout = self._module.params['timeout']

        try:
            self._zapi = ZabbixAPI(
                server_url,
                timeout=timeout,
                user=http_login_user,
                passwd=http_login_password
            )
            self._zapi.login(login_user, login_password)
        except Exception as e:
            self._module.fail_json(msg="Failed to connect to Zabbix server: %s" % e)

#!/usr/bin/python
# -*- coding: utf-8 -*-

"""Ansible module to import value maps into Zabbix"""

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.zabbix import AnsibleZabbix, zbx_argument_spec


DOCUMENTATION = '''
---
module: zabbix_valuemap
short_description: Import or remove zabbix value maps
description:
    - Imports or Deletes Zabbix value maps using the Zabbix API
options:
    name:
        required: false
        description:
            - Name of the valuemap to delete, not required on import
    valuemap_file:
        required: true
        description:
            - the xml file containing the value map definition
    state:
        required: false
        default: "present"
        choices: [ present, absent ]
        description:
            - Whether the value should be present or not on the zabbix server.
    server_url:
        description:
            - Url of Zabbix server, with protocol (http or https).
        required: true
        aliases: [ "url" ]
    login_user:
        description:
            - Zabbix api user name.
        required: true
    login_password:
        description:
            - Zabbix api user password.
        required: true
    http_login_user:
        description:
            - Basic Auth login
        required: false
        default: None
    http_login_password:
        description:
            - Basic Auth password
        required: false
        default: None
    timeout:
        description:
            - The timeout of API request (seconds).
        default: 10
'''

EXAMPLES = '''
# Example:
- name: Import Zabbix value maps
  zabbix_valuemap:
     server_url=http://zabbix_server/api_jsonrpc.php
     login_user=zabbix_username
     login_password=zabbix_password
     valuemap_file="valuemap.xml"
     state=present
'''

class ValueMap(AnsibleZabbix):
    """Return a valuemap class"""

    def __init__(self, module):
        super(ValueMap, self).__init__(module)
        self.state = module.params['state']
        self.valuemap_file = module.params['valuemap_file']
        self.name = module.params['name']


    def exists(self):
        """Check if valuemap exists, return boolean"""
        valuemap_list = self._zapi.valuemap.get({
            'output': 'extend',
            'filter': {
                'host': self.name
            }
        })
        if len(valuemap_list) < 1:
            return False
        else:
            return True

    def delete(self):
        """Delete valuemap, return boolean"""
        try:
            valuemap_id = self._zapi.valuemap.get({
                'output': 'extend',
                'filter': {
                    'host': self.name
                }
            })[0]['valuemapid']
            self._zapi.valuemap.delete([valuemap_id])
            return True
        except Exception as eret:
            self._module.fail_json(
                name=self.name,
                msg="Failed to delete valuemap id: %u ; error was: %s" % (valuemap_id, eret)
            )

    def create(self):
        """Create/Update valuemap, return boolean success value"""
        try:
            with open(self.valuemap_file, "r") as myfile:
                config = myfile.read()
        except:
            self._module.fail_json(
                msg="failed to read valuemap file: %s" % self.valuemap_file
            )

        importrules = {
            'valueMaps': {
                'createMissing' : True,
                'updateExisting': True,
            }
        }
        parameters = {'format': 'xml', 'source': config, 'rules': importrules}
        try:
            self._zapi.configuration.import_(parameters)
            return True
        except Exception as eret:
            self._module.fail_json(
                msg="failed to import valuemap: %s" % eret
            )


def main():
    """Do the needful"""
    argument_spec = zbx_argument_spec()
    argument_spec.update(dict(
        state=dict(default='present', choices=['present', 'absent'], type='str'),
        valuemap_file=dict(required=False, type='str'),
        name=dict(required=False, type='str'),
    ))
    module = AnsibleModule(
        argument_spec=argument_spec,
        # Don't support check mode for now
        supports_check_mode=False
    )

    valuemap = ValueMap(module)

    if valuemap.state == 'absent':
        if valuemap.exists():
            valuemap.delete()
            module.exit_json(
                changed=True,
                result="Successfully deleted valuemap %s" % valuemap.name
            )
    elif valuemap.state == 'present':
        valuemap.create()
        module.exit_json(
            changed=True,
            result="Successfully imported valuemap file %s" % valuemap.valuemap_file
        )

if __name__ == '__main__':
    main()

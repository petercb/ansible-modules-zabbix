#!/usr/bin/python
# -*- coding: utf-8 -*-

"""Ansible module to manipulate global macros in Zabbix"""

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.zabbix import AnsibleZabbix, zbx_argument_spec


DOCUMENTATION = '''
---
module: zabbix_globalmacro
short_description: Zabbix global macro creates/updates/deletes
description:
   - manages Zabbix global macros, it can create, update or delete them.
requirements:
    - "python >= 2.6"
    - zabbix-api
options:
    server_url:
        description:
            - Url of Zabbix server, with protocol (http or https).
        required: true
        aliases: [ "url" ]
    login_user:
        description:
            - Zabbix user name.
        required: true
    login_password:
        description:
            - Zabbix user password.
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
    macro_name:
        description:
            - Name of the global macro.
        required: true
    macro_value:
        description:
            - Value of the global macro.
        required: true
    state:
        description:
            - State of the macro.
            - On C(present), it will create if macro does not exist or update
              the macro if the associated data is different.
            - On C(absent) will remove a macro if it exists.
        required: false
        choices: ['present', 'absent']
        default: "present"
    timeout:
        description:
            - The timeout of API request (seconds).
        default: 10
'''

EXAMPLES = '''
- name: Create a new global macro or update an existing macro's value
  local_action:
    module: zabbix_globalmacro
    server_url: http://monitor.example.com
    login_user: username
    login_password: password
    macro_name: foo
    macro_value: bar
    state: present
'''

class GlobalMacro(AnsibleZabbix):
    """Return a Global Macro object"""
    def __init__(self, module):
        super(GlobalMacro, self).__init__(module)


    def get_global_macro(self, macro_name):
        """get global macro"""
        try:
            global_macro_list = self._zapi.usermacro.get({
                "globalmacro": True,
                "output": "extend",
                'filter': {
                    'macro': '{$' + macro_name + '}'
                }
            })
            if len(global_macro_list) > 0:
                return global_macro_list[0]
            return None
        except Exception as e:
            self._module.fail_json(msg="Failed to get global macro %s: %s" % (macro_name, e))

    def create_global_macro(self, macro_name, macro_value):
        """create global macro"""
        try:
            if self._module.check_mode:
                self._module.exit_json(changed=True)
            self._zapi.usermacro.createglobal({
                'macro': '{$' + macro_name + '}',
                'value': macro_value
            })
            self._module.exit_json(
                changed=True,
                result="Successfully added host macro %s " % macro_name
            )
        except Exception as e:
            self._module.fail_json(msg="Failed to create global macro %s: %s" % (macro_name, e))

    def update_global_macro(self, global_macro_obj, macro_name, macro_value):
        """update global macro"""
        global_macro_id = global_macro_obj['globalmacroid']
        if (
                global_macro_obj['macro'] == '{$'+macro_name+'}' and
                global_macro_obj['value'] == macro_value
            ):
            self._module.exit_json(
                changed=False,
                result="Global macro %s already up to date" % macro_name
            )
        try:
            if self._module.check_mode:
                self._module.exit_json(changed=True)
            self._zapi.usermacro.updateglobal({
                'globalmacroid': global_macro_id,
                'value': macro_value
            })
            self._module.exit_json(
                changed=True,
                result="Successfully updated global macro %s " % macro_name
            )
        except Exception as e:
            self._module.fail_json(msg="Failed to update global macro %s: %s" % (macro_name, e))

    def delete_global_macro(self, global_macro_obj, macro_name):
        """delete global macro"""
        global_macro_id = global_macro_obj['globalmacroid']
        try:
            if self._module.check_mode:
                self._module.exit_json(changed=True)
            self._zapi.usermacro.deleteglobal([global_macro_id])
            self._module.exit_json(
                changed=True,
                result="Successfully deleted global macro %s " % macro_name
            )
        except Exception as e:
            self._module.fail_json(msg="Failed to delete global macro %s: %s" % (macro_name, e))

def main():
    """Do the needful"""
    argument_spec = zbx_argument_spec()
    argument_spec.update(dict(
        macro_name=dict(type='str', required=True),
        macro_value=dict(type='str', required=True),
        state=dict(default="present", choices=['present', 'absent']),
    ))
    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True
    )

    macro_name = (module.params['macro_name']).upper()
    macro_value = module.params['macro_value']
    state = module.params['state']

    global_macro_class_obj = GlobalMacro(module)

    global_macro_obj = global_macro_class_obj.get_global_macro(macro_name)

    if state == 'absent':
        if not global_macro_obj:
            module.exit_json(changed=False, msg="Global Macro %s does not exist" % macro_name)
        else:
            # delete a macro
            global_macro_class_obj.delete_global_macro(global_macro_obj, macro_name)
    else:
        if not global_macro_obj:
            # create macro
            global_macro_class_obj.create_global_macro(macro_name, macro_value)
        else:
            # update macro
            global_macro_class_obj.update_global_macro(global_macro_obj, macro_name, macro_value)


if __name__ == '__main__':
    main()

#!/usr/bin/python
# -*- coding: utf-8 -*-

"""Ansible module to manipulate groups in Zabbix"""

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.zabbix import AnsibleZabbix, zbx_argument_spec


DOCUMENTATION = '''
---
module: zabbix_usergroup
short_description: Zabbix user group creates/updates/deletes
description:
   - manages Zabbix groups, it can create, update or delete them.
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
    name:
        description:
            - name of the group
        required: true
    debug_mode:
        description:
            - Whether debug mode is enabled or disabled
            - Possible values are: 
            - 0 : (default) disabled
            - 1 : enabled.
        required: false
    gui_access:
        description:
            - Frontend authentication method of the users in the group
            - Possible values: 
            - 0 : (default) use the system default authentication method
            - 1 : use internal authentication
            - 2 : disable access to the frontend
        required: false
    status:
        description:
            - Whether the user group is enabled or disabled
            - Possible values are:
            - 0 : (default) enabled
            - 1 : disabled
        required: false
    rights:
        description:
            - The host groups and privileges the group has
            - An array of dictionary entries in the form of:
            - [{'host_group': 'name', 'permission': 0}]
        required: false
    state:
        description:
            - State of the user
            - On C(present), it will create or update the group
            - On C(absent), it will remove the group
        required: false
        choices: ['present', 'absent']
        default: "present"
    timeout:
        description:
            - The timeout of API request (seconds).
        default: 10
'''

EXAMPLES = '''
- name: Create a new group or update an existing group
  local_action:
    module: zabbix_usergroup
    server_url: http://monitor.example.com
    login_user: username
    login_password: password
    name: 'Test group'
    rights:
      - host_group: 'Linux servers'
        permission: 1
    state: present
'''

class Group(AnsibleZabbix):
    """Return a Group object"""
    def __init__(self, module):
        super(Group, self).__init__(module)


    def get_host_group_id(self, host_group_name):
        """get host group ids by name"""
        try:
            group_list = self._zapi.hostgroup.get({
                'output': 'extend',
                'filter': {
                    'name': host_group_name
                }
            })
            if len(group_list) > 0:
                return group_list[0]['groupid']
            return None
        except Exception as e:
            self._module.fail_json(
                msg="Failed to lookup host group %s: %s" % (host_group_name, e)
            )

    def get_group(self):
        """get group"""
        group_name = self._module.params['name']
        try:
            group_list = self._zapi.usergroup.get({
                'output': 'extend',
                'filter': {
                    'name': group_name
                }
            })
            if len(group_list) > 0:
                return group_list[0]
            return None
        except Exception as e:
            self._module.fail_json(
                msg="Failed to get group %s: %s" % (group_name, e)
            )

    def create_group(self):
        """create group"""
        params = self._module.params
        try:
            if self._module.check_mode:
                self._module.exit_json(changed=True)
            self._zapi.usergroup.create({
                'name': params['name'],
                'debug_mode': params.get('debug_mode', 0),
                'gui_access': params.get('gui_access', 0),
                'user_status': params.get('status', 0),
                'rights': params.get('rights', [])
            })
            self._module.exit_json(
                changed=True,
                result="Successfully added group %s " % params['name']
            )
        except Exception as e:
            self._module.fail_json(
                msg="Failed to create group %s: %s" % (params['name'], e)
            )

    def update_group(self, group_obj):
        """update group"""
        params = self._module.params
        group_def = dict(
            usrgrpid=group_obj['usrgrpid'],
            name=params['name'] or group_obj['name'],
            rights=params.get('rights') or group_obj.get('rights', [])
        )
        if params.get('debug_mode') is None:
            group_def['debug_mode'] = group_obj.get('debug_mode', 0)
        else:
            group_def['debug_mode'] = params['debug_mode']

        if params.get('gui_access') is None:
            group_def['gui_access'] = group_obj.get('gui_access', 0)
        else:
            group_def['gui_access'] = params['gui_access']

        if params.get('status') is None:
            group_def['user_status'] = group_obj.get('user_status', 0)
        else:
            group_def['user_status'] = params['status']

        try:
            if self._module.check_mode:
                self._module.exit_json(changed=True)
            self._zapi.usergroup.update(group_def)
            self._module.exit_json(
                changed=True,
                result="Successfully updated user group %s " % params['name']
            )
        except Exception as e:
            self._module.fail_json(
                msg="Failed to update user group %s: %s" % (params['name'], e)
            )

    def delete_group(self, group_obj):
        """delete user group"""
        params = self._module.params
        try:
            if self._module.check_mode:
                self._module.exit_json(changed=True)
            self._zapi.usergroup.delete([group_obj['usrgrpid']])
            self._module.exit_json(
                changed=True,
                result="Successfully deleted user group %s " % params['name']
            )
        except Exception as e:
            self._module.fail_json(
                msg="Failed to delete user group %s: %s" % (params['name'], e)
            )


def main():
    """Do the needful"""
    argument_spec = zbx_argument_spec()
    argument_spec.update(dict(
        name=dict(type='str', required=True),
        debug_mode=dict(type='int', required=False, default=None, choices=[0, 1, 2]),
        gui_access=dict(type='int', required=False, default=None, choices=[0, 1, 2]),
        status=dict(type='int', required=False, default=None, choices=[0, 1]),
        rights=dict(type='list', required=False, default=[]),
        state=dict(default="present", choices=['present', 'absent']),
    ))
    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True
    )

    group_class_obj = Group(module)

    # Lookup and convert any hostgroup names to ids
    # Validate data structure
    for entry in module.params['rights']:
        if entry.get('host_group') is None:
            module.fail_json(msg="host_group value for rights is required")
        else:
            entry['id'] = group_class_obj.get_host_group_id(
                entry.pop('host_group', None)
            )
        if entry.get('permission') is None:
            module.fail_json(msg="Permission value for rights is required")
        elif entry['permission'] not in [0, 2, 3]:
            module.fail_json(
                msg="Value %s is not valid for permission right" % entry['permission']
            )

    group_obj = group_class_obj.get_group()

    if module.params['state'] == 'absent':
        if not group_obj:
            module.exit_json(
                changed=False,
                msg="Group %s does not exist" % module.params['name']
            )
        else:
            # delete a group
            group_class_obj.delete_group(group_obj)
    else:
        if not group_obj:
            # create group
            group_class_obj.create_group()
        else:
            # update group
            group_class_obj.update_group(group_obj)

if __name__ == '__main__':
    main()

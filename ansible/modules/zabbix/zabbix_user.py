#!/usr/bin/python
# -*- coding: utf-8 -*-

"""Ansible module to manipulate users in Zabbix"""

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.zabbix import AnsibleZabbix, zbx_argument_spec


DOCUMENTATION = '''
---
module: zabbix_user
short_description: Zabbix user creates/updates/deletes
description:
   - manages Zabbix users, it can create, update or delete them.
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
    user_alias:
        description:
            - Login name of the user
        required: true
    user_password:
        description:
            - Password to set for the user
            - Defaults to the same as their user_alias
        required: false
    user_groups:
        description:
            - Array of groups to add the user to
        required: false
        default: Guests
    user_name:
        description:
            - First name of the user
        required: false
    user_surname:
        description:
            - Surname of the user
        required: false
    user_type:
        description:
            - The type of the user
            - 1 - (default) regular user
            - 2 - Admin
            - 3 - Super Admin
        required: false
    state:
        description:
            - State of the user
            - On C(present), it will create or update the user
            - On C(absent), it will remove the user
        required: false
        choices: ['present', 'absent']
        default: "present"
    timeout:
        description:
            - The timeout of API request (seconds).
        default: 10
'''

EXAMPLES = '''
- name: Create a new user or update an existing user
  local_action:
    module: zabbix_user
    server_url: http://monitor.example.com
    login_user: username
    login_password: password
    user_alias: fbar
    user_name: Foo
    user_surname: Bar
    state: present
'''

class User(AnsibleZabbix):
    """Return a User object"""
    def __init__(self, module):
        super(User, self).__init__(module)


    def get_user(self):
        """get user"""
        user_alias = self._module.params['user_alias']
        try:
            user_list = self._zapi.user.get({
                "output": "extend",
                'filter': {
                    'alias': user_alias
                }
            })
            if len(user_list) > 0:
                return user_list[0]
            return None
        except Exception as e:
            self._module.fail_json(
                msg="Failed to get user %s: %s" % (user_alias, e)
            )

    def get_group(self, group_name):
        """get group"""
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

    def create_user(self, user_group_ids):
        """create user"""
        params = self._module.params
        user_def=dict(
            alias=params['user_alias'],
            usrgrps=user_group_ids or [{'usrgrpid': self.get_group('Guests')['usrgrpid']}]
        )
        if params.get('user_password') is None:
            self._module.fail_json(
                msg='Failed to create user %s : user_password not defined' % params['user_alias']
            )
        else:
            user_def['passwd'] = params['user_password']
        if params.get('user_name') is not None:
            user_def['name'] = params['user_name']
        if params.get('user_surname') is not None:
            user_def['surname'] = params['user_surname']
        if params.get('user_type') is not None:
            user_def['type'] = params['user_type']
        try:
            if self._module.check_mode:
                self._module.exit_json(changed=True)
            self._zapi.user.create(user_def)
            self._module.exit_json(
                changed=True,
                result="Successfully added user %s " % params['user_alias']
            )
        except Exception as e:
            self._module.fail_json(
                msg="Failed to create user %s: %s" % (params['user_alias'], e)
            )

    def update_user(self, user_obj, user_group_ids):
        """update user"""
        params = self._module.params
        user_alias = user_obj['alias']
        user_def = dict(userid=user_obj['userid'])
        if params.get('user_name') is not None:
            user_def['name'] = params['user_name']
        if params.get('user_surname') is not None:
            user_def['surname'] = params['user_surname']
        if params.get('user_type') is not None:
            user_def['type'] = params['user_type']
        if params.get('user_password') is not None:
            user_def['passwd'] = params['user_password']
        if user_group_ids:
            user_def['usrgrps'] = user_group_ids
        try:
            if self._module.check_mode:
                self._module.exit_json(changed=True)
            self._zapi.user.update(user_def)
            self._module.exit_json(
                changed=True,
                result="Successfully updated user %s " % user_alias
            )
        except Exception as e:
            self._module.fail_json(
                msg="Failed to update user %s: %s" % (user_alias, e)
            )

    def delete_user(self, user_obj):
        """delete user"""
        user_id = user_obj['userid']
        user_alias = user_obj['alias']
        try:
            if self._module.check_mode:
                self._module.exit_json(changed=True)
            self._zapi.user.delete([user_id])
            self._module.exit_json(
                changed=True,
                result="Successfully deleted user %s " % user_alias
            )
        except Exception as e:
            self._module.fail_json(
                msg="Failed to delete user %s: %s" % (user_alias, e)
            )

def main():
    """Do the needful"""
    argument_spec = zbx_argument_spec()
    argument_spec.update(dict(
        user_alias=dict(
            type='str',
            required=True
        ),
        user_password=dict(
            type='str',
            required=False,
            default=None,
            no_log=True
        ),
        user_name=dict(
            type='str',
            required=False,
            default=None
        ),
        user_surname=dict(
            type='str',
            required=False,
            default=None
        ),
        user_type=dict(
            type='int',
            required=False,
            default=None,
            choices=[1, 2, 3]
        ),
        user_groups=dict(
            type='list',
            required=False,
            default=None
        ),
        state=dict(
            default="present",
            choices=['present', 'absent']
        ),
    ))
    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True
    )

    user_class_obj = User(module)

    # Lookup and convert group names to ids
    user_group_ids = []
    if module.params.get('user_groups') is not None:
        for group_name in module.params['user_groups']:
            user_group_ids.append({
                'usrgrpid': user_class_obj.get_group(group_name)['usrgrpid']
            })

    user_obj = user_class_obj.get_user()

    if module.params['state'] == 'absent':
        if not user_obj:
            module.exit_json(
                changed=False,
                msg="User %s does not exist" % module.params['user_alias']
            )
        else:
            # delete a user
            user_class_obj.delete_user(user_obj)
    else:
        if not user_obj:
            # create user
            user_class_obj.create_user(user_group_ids)
        else:
            # update user
            user_class_obj.update_user(user_obj, user_group_ids)

if __name__ == '__main__':
    main()

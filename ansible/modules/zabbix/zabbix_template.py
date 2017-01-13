#!/usr/bin/python
# -*- coding: utf-8 -*-

"""Ansible module to manipulate Templates in Zabbix"""

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.zabbix import AnsibleZabbix, zbx_argument_spec


DOCUMENTATION = '''
---
module: zabbix_template
short_description: Zabbix Template import/update/delete
description:
   - manages Zabbix Templates, it can import, update or delete them.
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
    template_name:
        description:
            - Name of the template, required for delete or update
        required: false
    template_file:
        description:
            - the xml file containing the template
        required: false
    rename:
        description:
            - Change the name of an existing template
        required: false
    state:
        description:
            - State of the template
            - On C(present), it will import the Template
            - On C(absent) will remove the Template if it exists.
        required: false
        choices: ['present', 'absent']
        default: "present"
    timeout:
        description:
            - The timeout of API request (seconds).
        default: 10
'''

EXAMPLES = '''
- name: Import a new Template or update existing
  local_action:
    module: zabbix_template
    server_url: http://monitor.example.com
    login_user: username
    login_password: password
    template_file: zbx_foo.xml
    state: present
'''

class Template(AnsibleZabbix):
    """Return a Template object"""
    def __init__(self, module):
        super(Template, self).__init__(module)


    def get_template(self, template_name):
        """get template"""
        try:
            template_list = self._zapi.template.get({
                "output": "extend",
                'filter': {
                    'host': template_name
                }
            })
            if len(template_list) > 0:
                return template_list[0]
            return None
        except Exception as e:
            self._module.fail_json(msg="Failed to get Template %s: %s" % (template_name, e))


    def import_template(self, template_file):
        """import template"""
        try:
            with open(template_file, "r") as myfile:
                config = myfile.read()
        except:
            self.module.fail_json(
                msg="failed to read template file: %s" % self.template_file
            )

        importrules = {
            'applications': {
                'createMissing' : True,
                'updateExisting': True,
                'deleteMissing' : True,
            },
            'discoveryRules': {
                'createMissing' : True,
                'updateExisting': True,
                'deleteMissing' : True,
            },
            'graphs': {
                'createMissing' : True,
                'updateExisting': True,
                'deleteMissing' : True,
            },
            'groups': {
                'createMissing' : True,
            },
            'httptests': {
                'createMissing' : True,
                'updateExisting' : True,
                'deleteMissing' : True,
            },
            'items': {
                'createMissing' : True,
                'updateExisting': True,
                'deleteMissing' : True,
            },
            'templateLinkage': {
                'createMissing' : True,
            },
            'templates': {
                'createMissing' : True,
                'updateExisting': True,
            },
            'templateScreens': {
                'createMissing' : True,
                'updateExisting': True,
                'deleteMissing' : True,
            },
            'triggers': {
                'createMissing' : True,
                'updateExisting': True,
                'deleteMissing' : True,
            }
        }
        parameters = {'format': 'xml', 'source': config, 'rules': importrules}
        try:
            if self._module.check_mode:
                self._module.exit_json(changed=True)
            self._zapi.configuration.import_(parameters)
            self._module.exit_json(
                changed=True,
                result="Successfully imported template"
            )
        except Exception as e:
            self._module.fail_json(msg="Failed to import template: %s" % e)


    def rename_template(self, template_obj, rename):
        """rename template"""
        template_id = template_obj['templateid']
        try:
            if self._module.check_mode:
                self._module.exit_json(changed=True)
            self._zapi.template.update({
                'templateid': template_id,
                'host': rename,
                'name': rename
            })
            self._module.exit_json(
                changed=True,
                result="Successfully renamed template to %s " % rename
            )
        except Exception as e:
            self._module.fail_json(msg="Failed to rename template: %s" % e)

    def delete_template(self, template_obj, template_name):
        """delete template"""
        template_id = template_obj['templateid']
        try:
            if self._module.check_mode:
                self._module.exit_json(changed=True)
            self._zapi.template.delete([template_id])
            self._module.exit_json(
                changed=True,
                result="Successfully deleted template %s " % template_name
            )
        except Exception as e:
            self._module.fail_json(msg="Failed to delete template %s: %s" % (template_name, e))

def main():
    """Do the needful"""
    argument_spec = zbx_argument_spec()
    argument_spec.update(dict(
        template_file=dict(type='str', required=False, default=None),
        template_name=dict(type='str', required=False, default=None),
        rename=dict(type='str', required=False, default=None),
        state=dict(default="present", choices=['present', 'absent']),
    ))
    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True
    )

    try:
        template_class_obj = Template(module)
        state = module.params.get('state')
        template_file = module.params.get('template_file')
        template_name = module.params.get('template_name')
        rename = module.params.get('rename')

        if state == 'absent':
            if template_name is None:
                module.fail_json(msg="template_name is a required parameter on remove")
            else:
                template_obj = template_class_obj.get_template(template_name)
                if not template_obj:
                    module.exit_json(changed=False, msg="Template %s does not exist" % template_name)
                else:
                    # delete template
                    template_class_obj.delete_template(template_obj, template_name)
        elif state == 'present':
            if template_file is not None:
                # import template
                template_class_obj.import_template(template_file)
            elif (template_name is not None and rename is not None):
                template_obj = template_class_obj.get_template(template_name)
                if not template_obj:
                    module.exit_json(changed=False, msg="Template %s does not exist" % template_name)
                else:
                    # rename the template
                    template_class_obj.rename_template(template_obj, rename)
            else:
                # unknown operation
                module.fail_json(msg="Either template_file or template_name must be set")
        else:
            module.fail_json(msg="Unknown state: %s" % state)

    except Exception as e:
        module.fail_json(msg='Failed to retrieve template object')

if __name__ == '__main__':
    main()

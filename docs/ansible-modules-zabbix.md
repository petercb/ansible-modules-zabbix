# Ansible Zabbix modules

---
### Requirements
* zabbix-api python module

---
### Modules

  * [zabbix_template - zabbix template import/update/delete](#zabbix_template)
  * [zabbix_user - zabbix user creates/updates/deletes](#zabbix_user)
  * [zabbix_usergroup - zabbix user group creates/updates/deletes](#zabbix_usergroup)
  * [zabbix_valuemap - import or remove zabbix value maps](#zabbix_valuemap)
  * [zabbix_globalmacro - zabbix global macro creates/updates/deletes](#zabbix_globalmacro)

---

## zabbix_template
Zabbix Template import/update/delete

  * Synopsis
  * Options
  * Examples

#### Synopsis
 manages Zabbix Templates, it can import, update or delete them.

#### Options

| Parameter     | required    | default  | choices    | comments |
| ------------- |-------------| ---------|----------- |--------- |
| rename  |   no  |  | |  Change the name of an existing template  |
| http_login_password  |   no  |    | |  Basic Auth password  |
| template_file  |   no  |  | |  the xml file containing the template  |
| login_user  |   yes  |  | |  Zabbix user name.  |
| template_name  |   no  |  | |  Name of the template, required for delete or update  |
| http_login_user  |   no  |    | |  Basic Auth login  |
| server_url  |   yes  |  | |  Url of Zabbix server, with protocol (http or https).  |
| state  |   no  |  present  | <ul> <li>present</li>  <li>absent</li> </ul> |  State of the template  On C(present), it will import the Template  On C(absent) will remove the Template if it exists.  |
| timeout  |   |  10  | |  The timeout of API request (seconds).  |
| login_password  |   yes  |  | |  Zabbix user password.  |


 
#### Examples

```
- name: Import a new Template or update existing
  local_action:
    module: zabbix_template
    server_url: http://monitor.example.com
    login_user: username
    login_password: password
    template_file: zbx_foo.xml
    state: present

```



---


## zabbix_user
Zabbix user creates/updates/deletes

  * Synopsis
  * Options
  * Examples

#### Synopsis
 manages Zabbix users, it can create, update or delete them.

#### Options

| Parameter     | required    | default  | choices    | comments |
| ------------- |-------------| ---------|----------- |--------- |
| http_login_password  |   no  |    | |  Basic Auth password  |
| login_user  |   yes  |  | |  Zabbix api user name.  |
| user_password  |   no  |  | |  Password to set for the user  Defaults to the same as their user_alias  |
| http_login_user  |   no  |    | |  Basic Auth login  |
| user_type  |   no  |  | |  The type of the user  1 - (default) regular user  2 - Admin  3 - Super Admin  |
| server_url  |   yes  |  | |  Url of Zabbix server, with protocol (http or https).  |
| state  |   no  |  present  | <ul> <li>present</li>  <li>absent</li> </ul> |  State of the user  On C(present), it will create or update the user  On C(absent), it will remove the user  |
| timeout  |   |  10  | |  The timeout of API request (seconds).  |
| login_password  |   yes  |  | |  Zabbix api user password.  |
| user_alias  |   yes  |  | |  Login name of the user  |
| user_surname  |   no  |  | |  Surname of the user  |
| user_groups  |   no  |  Guests  | |  Array of groups to add the user to  |
| user_name  |   no  |  | |  First name of the user  |


 
#### Examples

```
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

```



---


## zabbix_usergroup
Zabbix user group creates/updates/deletes

  * Synopsis
  * Options
  * Examples

#### Synopsis
 manages Zabbix groups, it can create, update or delete them.

#### Options

| Parameter     | required    | default  | choices    | comments |
| ------------- |-------------| ---------|----------- |--------- |
| status  |   no  |  | |  Whether the user group is enabled or disabled  Possible values are  0 - (default) enabled  1 - disabled  |
| http_login_password  |   no  |    | |  Basic Auth password  |
| name  |   yes  |  | |  name of the group  |
| rights  |   no  |  | |  The host groups and privileges the group has  An array of dictionary entries in the form of  [{'host_group': 'name', 'permission': 0}]  |
| login_user  |   yes  |  | |  Zabbix api user name.  |
| http_login_user  |   no  |    | |  Basic Auth login  |
| server_url  |   yes  |  | |  Url of Zabbix server, with protocol (http or https).  |
| state  |   no  |  present  | <ul> <li>present</li>  <li>absent</li> </ul> |  State of the user  On C(present), it will create or update the group  On C(absent), it will remove the group  |
| debug_mode  |   no  |  | |  Whether debug mode is enabled or disabled  Possible values are  0 - (default) disabled  1 - enabled.  |
| timeout  |   |  10  | |  The timeout of API request (seconds).  |
| login_password  |   yes  |  | |  Zabbix api user password.  |
| gui_access  |   no  |  | |  Frontend authentication method of the users in the group  Possible values  0 - (default) use the system default authentication method  1 - use internal authentication  2 - disable access to the frontend  |


 
#### Examples

```
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

```



---


## zabbix_valuemap
Import or remove zabbix value maps

  * Synopsis
  * Options
  * Examples

#### Synopsis
 Imports or Deletes Zabbix value maps using the Zabbix API

#### Options

| Parameter     | required    | default  | choices    | comments |
| ------------- |-------------| ---------|----------- |--------- |
| http_login_password  |   no  |    | |  Basic Auth password  |
| name  |   no  |  | |  Name of the valuemap to delete, not required on import  |
| login_user  |   yes  |  | |  Zabbix api user name.  |
| http_login_user  |   no  |    | |  Basic Auth login  |
| valuemap_file  |   yes  |  | |  the xml file containing the value map definition  |
| server_url  |   yes  |  | |  Url of Zabbix server, with protocol (http or https).  |
| state  |   no  |  present  | <ul> <li>present</li>  <li>absent</li> </ul> |  Whether the value should be present or not on the zabbix server.  |
| timeout  |   |  10  | |  The timeout of API request (seconds).  |
| login_password  |   yes  |  | |  Zabbix api user password.  |


 
#### Examples

```
# Example:
- name: Import Zabbix value maps
  zabbix_valuemap:
     server_url=http://zabbix_server/api_jsonrpc.php
     login_user=zabbix_username
     login_password=zabbix_password
     valuemap_file="valuemap.xml"
     state=present

```



---


## zabbix_globalmacro
Zabbix global macro creates/updates/deletes

  * Synopsis
  * Options
  * Examples

#### Synopsis
 manages Zabbix global macros, it can create, update or delete them.

#### Options

| Parameter     | required    | default  | choices    | comments |
| ------------- |-------------| ---------|----------- |--------- |
| http_login_password  |   no  |    | |  Basic Auth password  |
| macro_name  |   yes  |  | |  Name of the global macro.  |
| macro_value  |   yes  |  | |  Value of the global macro.  |
| login_user  |   yes  |  | |  Zabbix user name.  |
| http_login_user  |   no  |    | |  Basic Auth login  |
| server_url  |   yes  |  | |  Url of Zabbix server, with protocol (http or https).  |
| state  |   no  |  present  | <ul> <li>present</li>  <li>absent</li> </ul> |  State of the macro.  On C(present), it will create if macro does not exist or update the macro if the associated data is different.  On C(absent) will remove a macro if it exists.  |
| timeout  |   |  10  | |  The timeout of API request (seconds).  |
| login_password  |   yes  |  | |  Zabbix user password.  |


 
#### Examples

```
- name: Create a new global macro or update an existing macro's value
  local_action:
    module: zabbix_globalmacro
    server_url: http://monitor.example.com
    login_user: username
    login_password: password
    macro_name: foo
    macro_value: bar
    state: present

```



---


---
Modified: 2017-01-12 15:19:27 EST

# Ansible Collection - federstedt.librenms

Ansible Collection for LibreNMS API.

Currently in early development, I've implemented add, delete and get modules for the "/devices" endpoint.  
Developed since I wanted to learn how to develop my own modules, and also needed the functionality for a project.    
Will add more if I find the time / need.

## Requirements
- Python 3.8
- Python modules:
  - 'requests'
- Ansible 2.9.6 (could work with earlier but I tested with this version)

## Installation
```ansible-galaxy collection install federstedt.librenms```

## Modules
```libre_devices``` Add / remove devices using "state" : "present" / "absent".  
```libre_devices_info``` get info from devices API.  


## Usage
See playbooks/ in github repo for more examples.

Sample for getting **all devices**:
```
- name: Example librenms get
  hosts: localhost
  gather_facts: false
  vars_files:
    - vars/libre.yml
  tasks:
   - name: Get all devices.
     federstedt.librenms.libre_devices_info:
      api_url: "{{ api_url }}"
      api_token: "{{ api_token }}"
     register: testout
   - name: Dump output
     ansible.builtin.debug:
      msg: '{{ testout }}'
```
**Add device**:
```
- name: Example librenms add device.
  hosts: localhost
  gather_facts: false
  vars_files:
    - vars/libre.yml
  tasks:
   - name: Post device to LibreNMS
     federstedt.librenms.libre_devices:
      state: present
      api_url: "{{ api_url }}"
      api_token: "{{ api_token }}"
      hostname: localhost.localdomain
      snmpver: v1
      community: public
      force_add: true
```
**Delete device**:
```
- name: Example librenms delete device.
  hosts: localhost
  gather_facts: false
  vars_files:
    - vars/libre.yml
  tasks:
   - name: Delete device from LibreNMS
     federstedt.librenms.libre_devices:
      state: absent
      api_url: "{{ api_url }}"
      api_token: "{{ api_token }}"
      hostname: localhost.localdomain
```
**Filtered search**:  
Doing filtered searches on libreNMS is not that straightforward at the moment.  
Use this as referense: https://docs.librenms.org/API/Devices/#input  
Follow above link and set type and query as documented. In my tests multiple filters would not work.
```
- name: Example librenms get
  hosts: localhost
  gather_facts: false
  vars_files:
    - vars/libre.yml
  tasks:
   - name: Get a specific device.
     federstedt.librenms.libre_devices_info:
      api_url: "{{ api_url }}"
      api_token: "{{ api_token }}"
      query_params:
       - type: os
       - query: arubaos
     register: testout
   - name: Dump output
     ansible.builtin.debug:
      msg: '{{ testout }}'
```
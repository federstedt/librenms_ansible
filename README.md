# Ansible Collection - federstedt.librenms
---

Ansible Collection for LibreNMS API.

Developed since I wanted to learn devolping my own modules, and also needed the functionality for a project.  
Currently in early development, I've implemented add, delete and get modules for the /devices endpoint.  
Will add more if I find the time / need.

## Requirements
- Python 3.10
- Python modules:
  - 'requests'
- Ansible 2.9.10 (could work with earlier but I tested with this version)

## Installation
```ansible-galaxy collection install federstedt.librenms```

## Modules
```libre_devices``` Add / remove devices using "state" : "present" / "absent".  
```libre_devices_info``` get info from devices API.  


## Usage
See playbooks/ for more examples.

Sample for getting all devices:
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

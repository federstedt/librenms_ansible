#!/usr/bin/python

# Copyright: (c) 2023, Daniel Federstedt <daniel@braveops.se>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = r'''
---
module: libre_devices_info

short_description: Get device(s) to LibreNMS.

version_added: "1.0.0"

description: Run API GET methods to LibreNMS "devices" endpoint. https://docs.librenms.org/API/Devices/. Add, get or delete devices.

options:
    api_url:
        description: URL of the LibreNMS-server.
        required: true
        type: str
    api_token:
        description: API-token that should be used for authenticating to the LibreNMS API.
        required: true
        type: str
    ssl_verify:
        description: Sets if the host should check if the SSL-certificate of the LibreNMS-server is valid.
        required: false
        default: false
        type: bool
    query_params:
        description:
                - List of parameters passed to the query. Se examples: https://docs.librenms.org/API/Devices/#list_devices
        type: list
        elements: str
        default: []

# Specify this value according to your collection
# in format of namespace.collection.doc_fragment_name
extends_documentation_fragment:
    - my_namespace.my_collection.my_doc_fragment_name

author:
    - Daniel Federstedt (@federstedt)
'''

EXAMPLES = r'''

tasks:
    - name: Get device information
      libre_devices_info:
        name: some_device_hostname

        
Examples of how to use query filter.
Complete Syntax can be found at librenms API docu: https://docs.librenms.org/API/Devices/#list_devices

filter by os:
- name: Get a specific device.
     libre_devices_info:
      query_params:
       - type: os
       - query: arubaos

filter by status down:
   - name: Get a specific device.
     libre_devices_info:
      query_params:
       - type: down
'''

RETURN = r'''
data:
    description: The data returned by the request.
    returned: On success
'''

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.librenms_api_client import LibreClient, LibreAPIError
from ansible.module_utils.libre_utils import get_required_args, validate_args, parse_ansible_listdict

# define available arguments/parameters a user can pass to the module
module_args = {
        "api_url": {"type": "str", "required": True},
        "api_token": {"type": "str", "required": True},
        "ssl_verify": {"type": "bool", "required": False},

        # Arguments for getting a device
        "name": {"type": "str", "required": False, "aliases": ["hostname"]},
        "query_params": {"type": "list", "elements": "str", "default": []}
    }

module = AnsibleModule(argument_spec=module_args)


def device_get(params) ->dict:
    """
    Function gets device(s) from LibreNMS.

    Args:
        params(AnsibleModule.params): Provide AnsibleModule params 
            supplied by the run_module function.

    Returns:
        dict(changed , data): dict containing keys: 
            changed: False (since this is a get request),
            data: response(json_response from api_client).
    """
    if params['name']:
        endpoint = 'devices/' + params['name']
    else:
        endpoint = 'devices'

    if params['query_params']:
        query_params = parse_ansible_listdict(params['query_params'])
    else:
        query_params=None

    try:
        api_client = LibreClient(
            api_url=params['api_url'], api_token=params['api_token'],
            ssl_verify=params['ssl_verify'])
        response = api_client.get(endpoint=endpoint, params=query_params)
        return {"changed": False, "data" : response}
    except LibreAPIError as exc:
        raise Exception(str(exc.details)) from exc


def run_module():
    """
    Run module to get info from API.
    """
    module.params['state'] = 'get'

    # Validate that all required params are provided, based on state type.
    if not validate_args(module.params):
        module.fail_json(
            msg=f"Required argument(s) missing requires: {get_required_args(module.params['state'])}")


    try:
        response = device_get(module.params)

        module.exit_json(**response)
    except Exception as exc:
        module.fail_json(msg=str(exc))

def main():
    """
    Run the module.
    """
    run_module()


if __name__ == '__main__':
    main()

#!/usr/bin/python

# Copyright: (c) 2023, Daniel Federstedt <daniel@braveops.se>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
---
module: libre_devices

short_description: Add a device to LibreNMS.

version_added: "1.0.0"

description: Run API methods to LibreNMS "devices" endpoint. https://docs.librenms.org/API/Devices/. Add, get or delete devices.

options:
    state:
        description: State to implement. valid choices are: present or absent.
        required: true
        type: str
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
    name:
        alias: hostname
        desciption: Device hostname either ip-address or FQDN (localhost.localdomain) when adding. When doing get or delete: hostname can be either the device hostname or id.
        required: true, when adding or removing device, optional for get (if empty on get, returns all devices).
        type: str
    display: 
        description: A string to display as the name of this device
        required: false
        type: str
    port:
        description: SNMP port (defaults to port defined in config).
        required: false
        type: int
    transport:
        description: SNMP protocol (defaults to transport defined in config).
        required: false
        type: str
    snmpver:
        description: SNMP version to use, v1, v2c or v3. Defaults to v2c.
        default: v2c
        required: true, when adding device.
        type: str
    port_association_mode:
        description: method to identify ports: ifIndex (default), ifName, ifDescr, ifAlias
        required: false
        default: ifIndex
        type: str
    poller_group:
        description: This is the poller_group id used for distributed poller setup. Defaults to 0.
        required: false
        type: int
    force_add:
        description: Set to true to force the device to be added regardless of it being able to respond to snmp or icmp.
        required: false
        type: bool
        default: false
    community: 
        description: snmp community , required for SNMP v1 or v2c.
        required: false
        type: str
    authlevel:
        description: SNMPv3 authlevel (noAuthNoPriv, authNoPriv, authPriv).
        required: false
        type: str
    authname:
        description: SNMPv3 Auth username.
        required: false
        type: str
    authpass:
        description: SNMPv3 Auth password.
        required: false
        type: str
    authalgo:
        description: SNMPv3 Auth algorithm (MD5, SHA) (SHA-224, SHA-256, SHA-384, SHA-512 if supported by your server).
        required: false
        type: str
    cryptopass:
        description: SNMPv3 Crypto Password.
        required: false
        type: str
    cryptoalgo:
        description: SNMPv3 Crypto algorithm (AES, DES).
        required: false
        type: str    
    snmp_disable: 
        description: Boolean, set to true for ICMP only.
        required: false
        type: bool
    os:
        description: OS short name for the device (defaults to ping). (ICMP only)
        required: false
        type: str
    sysName:
        description: sysName for the device. (ICMP only)
        required: false
        type: str
    hardware:
        desciption: Device hardware. (ICMP only)
        required: false
        type: str
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
"""

EXAMPLES = r"""
tasks:
- name: Add a device
  libre_devices:
    state: present
    name: "192.168.1.1"
    display: "switch1"
    community: "public"

- name: Get a device
  libre_devices:
    state: get
    name: "192.168.1.1"

- name: Delete a device
  libre_devices:
    state: absent
    name: "192.168.1.1"

Example of how to use query filter.
Complete Syntax can be found at librenms API docu: https://docs.librenms.org/API/Devices/#list_devices

filter by os:
- name: Get a specific device.
     libre_devices:
      state: get
      query_params:
       - type: os
       - query: arubaos

filter by status down:
   - name: Get a specific device.
     libre_devices:
      state: get
      query_params:
       - type: down
"""

RETURN = r"""
data:
    description: The data returned by the request.
    returned: On success
"""

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.librenms_api_client import LibreClient, LibreAPIError
from ansible.module_utils.libre_utils import (
    get_required_args,
    validate_args,
    parse_json,
)

# define available arguments/parameters a user can pass to the module
module_args = {
    # Generic arguments
    "state": {"type": "str", "choices": ["present", "absent", "get"], "required": True},
    "api_url": {"type": "str", "required": True},
    "api_token": {"type": "str", "required": True},
    "ssl_verify": {"type": "bool", "required": False},
    # Argumens for adding a device
    "name": {"type": "str", "required": False, "aliases": ["hostname"]},
    "display": {"type": "str", "required": False},
    "port": {"type": "int", "required": False},
    "transport": {"type": "str", "required": False},
    "snmpver": {"type": "str", "required": False},
    "port_association_mode": {"type": "str", "required": False},
    "poller_group": {"type": "int", "required": False},
    "force_add": {"type": "bool", "required": False},
    "community": {"type": "str", "required": False},
    # Arguments for SNMPv3
    "authlevel": {"type": "str", "required": False},
    "authname": {"type": "str", "required": False},
    "authpass": {"type": "str", "required": False},
    "authalgo": {"type": "str", "required": False},
    "cryptopass": {"type": "str", "required": False},
    "cryptoalgo": {"type": "str", "required": False},
    # Arguments for Ping only / overrides
    "snmp_disable": {"type": "bool", "required": False},
    "os": {"type": "str", "required": False},
    "sysName": {"type": "str", "required": False},
    "hardware": {"type": "str", "required": False},
}

module = AnsibleModule(argument_spec=module_args)


def device_delete(params) -> dict:
    """
    Function deletes device from LibreNMS.

    Args:
        params(AnsibleModule.params): Provide AnsibleModule params
            supplied by the run_module function.

    Returns:
        dict(changed , data): dict containing keys:
            changed: True/False , data: response(json_response from api_client)
    """
    hostname = params["name"]
    try:
        api_client = LibreClient(
            api_url=params["api_url"],
            api_token=params["api_token"],
            ssl_verify=params["ssl_verify"],
        )

        response = api_client.delete(endpoint=f"devices/{hostname}")
        return {"changed": True, "data": response}

    except LibreAPIError as exc:
        if "not found" in exc.details:  # if device is not found, it is absent already.
            return {"changed": False, "data": exc.details}
        raise Exception(str(exc)) from exc

    except Exception as exc:
        raise Exception(str(exc)) from exc


def device_add(params) -> dict:
    """
    Function adds device to libreNMS.

    Args:
        params(AnsibleModule.params): Provide AnsibleModule params
            supplied by the run_module function.

    Returns:
        dict(changed , data): dict containing keys:
            changed: True/False , data: response(json_response from api_client)
    """

    try:
        api_client = LibreClient(
            api_url=params["api_url"],
            api_token=params["api_token"],
            ssl_verify=params["ssl_verify"],
        )

        json_data = parse_json(params=params)

        response = api_client.post(endpoint="devices", data=json_data)

        return {"changed": True, "data": response}

    except LibreAPIError as exc:
        if (
            "already exists" in exc.details
        ):  # if device already exist its already present.
            return {"changed": False, "data": exc.details}
        raise Exception(str(exc)) from exc

    except Exception as exc:
        raise Exception(str(exc)) from exc


def run_module():
    """
    run module, run get,post och delete to LibreNMS API.
    """

    # Validate that all required params are provided, based on state type.
    if not validate_args(module.params):
        module.fail_json(
            msg=f"Required argument(s) missing for state={module.params['state']}, requires: {get_required_args(module.params['state'])}"
        )

    try:
        if module.params["state"] == "present":
            response = device_add(module.params)
        elif module.params["state"] == "absent":
            response = device_delete(module.params)
        else:
            module.fail_json(msg=f"Invalid state provided: {module.params['state']}")

        module.exit_json(**response)
    except Exception as exc:
        module.fail_json(msg=str(exc))


def main():
    """
    Run the module.
    """
    run_module()


if __name__ == "__main__":
    main()

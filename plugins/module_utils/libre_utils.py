"""
Common utils used by libreNMS modules.
"""
import json

def get_required_args(state):
    """
    Map required arguments to state.

    Args:
        state(str): state from module.

    Returns:
        required_args(list): list of required args.
    """
    required_args_map = {
        'present': ['name', 'snmpver'],
        'get': [],  # Tom lista eftersom det inte krävs några argument för get_device
        'absent': ['name']
    }

    return required_args_map.get(state, [])

def validate_args(params) ->bool:
    """
    Validate which args are required based on state.

    Args:
        params(AnsibleModule.params): Provide AnsibleModule params 
            supplied by the run_module function
    
    Returns:
        True/False(bool): if a required param is missing return: False
            else return True.
    """
    state = params['state']
    required_args = get_required_args(state)
    for arg in required_args:
        if arg not in params or params[arg] is None:
            return False
    return True

def parse_json(params) ->dict:
    """
    Parse params to json_data for requests call to API.

    Args:
        params(AnsibleModule.params): Provide AnsibleModule params 
            supplied by the run_module function.

    Returns:
        json_data(dict): json_data prepered for API-call to LibreNMS.
    """
    json_data = {
        "hostname": params['name'],
        "display" : params['display'],
        "port": params['port'],
        "transport" : params['transport'],
        "snmpver" : params['snmpver'],
        "port_association_mode": params['port_association_mode'],
        "poller_group" : params['poller_group'],
        "force_add" : params['force_add'],
        "community": params['community'],
        'authlevel' : params['authlevel'],
        'authname' : params['authname'],
        'authpass' : params['authpass'],
        'authalgo' : params['authalgo'],
        'cryptopass' : params['cryptopass'],
        'cryptoalgo' : params['cryptoalgo'],
        'snmp_disable' : params['snmp_disable'],
        'os' : params['os'],
        'sysName' : params['sysName'],
        'hardware' : params['hardware']
    }
    return json_data

def parse_ansible_listdict(data)->dict:
    """
    Unpack a list of dict and return a dict instead.

    Args: data(list): a list containing dicts: [{key:value},{key:value}], 
        but since it's ansible formated the dicts are actually strings.

    Returns:
        formated_data(dict): a dict of key value pairs.
    """
    formated_dict = {}
    for entry in data:
        entry = entry.replace("'", '"')
        entry_dict = json.loads(entry)
        for key, value in entry_dict.items():
            formated_dict[key] = value

    return formated_dict

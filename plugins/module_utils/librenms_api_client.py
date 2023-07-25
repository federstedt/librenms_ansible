"""
REST-API Client for librenms.
https://docs.librenms.org/API/Devices/#endpoint-categories
"""
import requests

class LibreAPIError(Exception):
    """
    Exception encountered talking to API.
    """
    def __init__(self, status_code, details)->None:
        self.status_code = status_code
        self.details = details

class LibreClient():
    """
    rest-api client object.
    Uses reuests to send/recieve data to librenms.
    """
    def __init__(self, api_url, api_token, ssl_verify=False)->None:
        self.api_url = api_url
        self.api_token = api_token
        self.ssl_verify = ssl_verify
        self.session = None

    def invoke(self, method, endpoint, json_data=None, params=None) ->requests.Response:
        """
        Invoke command to endpoint. 

        Args:
            method(str): GET, PUT, DELETE . Must be valid requests command.

        Returns:
            response(requests.Response): data from endpoint.
        """
        headers = {
        "X-Auth-Token": self.api_token
        }
        url = f"{self.api_url}/api/v0/{endpoint}"

        if self.session is None:
            self.session = requests.session()
        try:
            if json_data:
                headers["Content-Type"] = "application/json"

            response = self.session.request(
                method=method,url=url,headers=headers,
                json=json_data, verify=self.ssl_verify, params=params)
            response.raise_for_status()
        except requests.exceptions.Timeout as exc:
            raise LibreAPIError(408, "The request has timed out") from exc
        except requests.exceptions.HTTPError as exc:
            raise LibreAPIError(exc.response.status_code, response.json()['message']) from exc
        except requests.exceptions.RequestException as exc:
            raise LibreAPIError(500, str(exc)) from exc

        return response

    def get(self, endpoint, params=None)-> dict:
        """
        Use invoke class method to get data from API.

        Returns:
            jons_data(dict): data from api.
        """
        #TODO: fix pagination och offset ifall det finns i APIt
        response = self.invoke("GET",endpoint=endpoint, params=params)
        if response.status_code != 200:
            raise LibreAPIError(status_code=response.status_code,
                                details=f'Failed to get {endpoint} from LibreNMS API.\n{response.json["message"]}')
        json_resp = response.json()
        return json_resp

    def post(self, endpoint, data) -> dict:
        """
        Use invoke class method to post data to API.

        Args:
            endpoint(str): endpoint at libreNMS API, for example 'devices'.
            data(str/dict): data should be dict formatted 
            but to support ansible post it can be a string containing a dict.

        Returns:
            josn_resp(dict): Response from API after post reuqest finished.

        https://docs.librenms.org/API/Devices/#add_device
        """
        response = self.invoke("POST", endpoint=endpoint, json_data=data)
        if response.status_code not in [200, 500]:
            if response.status_code == 500 and 'already exists' not in response.json["message"]:
                raise LibreAPIError(500, details=f'Failed to POST to {endpoint}.\n{response.json["message"]}')
            else:
                # this happens if data already exists
                pass
        json_resp = response.json()
        return json_resp

    def delete(self, endpoint, data=None) ->dict:
        """
        Use invoke class methoed to delete datra from API.

        Args:
            endpoint(str): endpoint to use delete method.
            data(dict): see API docu for required args.(default is None)

        Returns:
            json_resp(dict): Response from API after delete call finished.
        """
        response = self.invoke("DELETE", endpoint=endpoint, json_data=data)
        if response.status_code not in [200]:
            raise LibreAPIError(response.status_code,
                                details=f'Failed to DELETE at {endpoint}.\n{response.json["message"]}'
                                )
        json_resp = response.json()
        return json_resp

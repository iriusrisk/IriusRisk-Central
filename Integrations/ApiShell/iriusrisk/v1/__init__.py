"""This module contains helper methods for calling the IriusRisk API.
"""

import http.client
import json
import logging
from urllib.parse import quote
from iriusrisk import get_config, get_connection

__all__=["do_get", "do_put", "do_post", "do_delete", "call_endpoint"]

# Provides helper methods that make accessing the IriusRisk v1 API easier.
_log = logging.getLogger('iriusrisk.v1')

def _build_path(path, encode_path):
    if type(path) is str:
        if encode_path:
            path = path.split("/")
        else:
            return path

    if encode_path:
        elements = []

        for element in path:
            elements.append(quote(element))

        path = elements

    return "/".join(path)

def call_endpoint(path, verb, headers={}, body=None, convert_response=True, encode_path=False):
    """Call a named endpoint of the IriusRisk API.

    Arguments:
    path            : the endpoint path. May be a collection of strings, each element
                      another call depth. So to call the URL
                      "/api/v1/products/:productid/threats," you would pass three 
                      elements in the collection, ["products", f"{productid}", "threats"]
    verb            : the verb when calling the endpoint, for instance GET, PUT, POST etc
    headers         : (optional) any headers to include on the call
    params          : (optional) any parameters to include on the call
    convert_response: (default: True): whether the response should be converted to JSON
    encode_path     : (default: False): whether URL encoding should be applied to the
                      various elements of the path.

    The method returns a tuple containing the HTTP response and data returned as the body
    of the response. The type of the data depends on two things. First, if convert_response
    is False, plain text is returned. Otherwise, it depends on the return type of the 
    API call. If (for instance) the return type is "application/json," then a json object
    is returned.
    """
    path = _build_path(path, encode_path)
    _log.info(f"Calling endpoint {path} with verb {verb}")

    config = get_config()

    if not "api-token" in headers:
        if config.key:
            headers["api-token"] = config.key
        else:
            _log.info("No API key was provided to this application; API call will likely fail")        

    if not "accept" in headers:
        headers["accept"] = "application/json"

    path = f"/api/v1/{path}"
    _log.debug(f"Making a {verb} call to {path} at {config.url}")
    conn = get_connection(config.url)

    if config.dryrun:
        resp = None
    else :
        conn.request(verb, path, body, headers)
        resp = conn.getresponse()

    result = None
    if convert_response and not config.dryrun:
        data = resp.read().decode("utf-8")
        if resp.status == 200 and headers["accept"] == "application/json":
            result = json.loads(data)
        else:
            result = data

    return (resp, result)

"""Call the specified endpoint using "GET."
"""
def do_get(path, headers={}, convert_response=True, encode_path=False):
    """Call the indicated endpoint via GET. See call_endpoint for more details."""
    return call_endpoint(path, "GET", headers, None, convert_response, encode_path)

def do_put(path, body, headers={}, convert_response=True, encode_path=False):
    return call_endpoint(path, "PUT", headers, body, convert_response, encode_path)

def do_post(path, body, headers={}, convert_response=True, encode_path=False):
    return call_endpoint(path, "POST", headers, body, convert_response, encode_path)

def do_delete(path, headers={}, convert_response=True, encode_path=False):
    return call_endpoint(path, "DELETE", headers, None, convert_response, encode_path)

import http.client
import json
from iriusrisk.v1 import *

# Provides helper methods that make accessing the IriusRisk v1 API easier.

def call_endpoint(path, verb, headers={}, params={}, convert_response=True):
    log.info(f"Calling endpoint {path} with verb {verb}")

    if not "api-token" in headers:
        if config.key:
            headers["api-token"] = config.key
        else:
            log.info("No API key was provided to this application; API call will likely fail")        

    if not "accept" in headers:
        headers["accept"] = "application/json"

    path = f"/api/v1/{path}"
    log.debug("Making a {verb} call to {path} at {config.url}")
    conn = http.client.HTTPSConnection(config.url)

    if config.dryrun:
        resp = None
    else :
        conn.request(verb, path, params, headers)
        resp = conn.getresponse()

    result = None
    if convert_response and not config.dryrun:
        data = resp.read().decode("utf-8")
        if resp.status == 200 and headers["accept"] == "application/json":
            result = json.loads(data)
        else:
            result = data

    return (resp, result)

def do_get(path, headers={}, params={}, convert_response=True):
    return call_endpoint(path, "GET", headers, params, convert_response)
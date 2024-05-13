import iriusrisk.commandline
import logging
import urllib.parse
import requests

class Multipart:
    def __init__(self, name, encoding, payload):
        self.name = name
        self.encoding = encoding
        self.payload = payload

_log = logging.getLogger(__name__)
__all__ = [ "get_target_url", "get_standards_from_instance", "do_get", "do_post", "do_put", "do_delete", "escape_text", "get_standards_from_file", "Multipart" ]

_resolved_url = None
_proxy_parameters_initialized = False
_proxy_parameters = None


def _get_proxy_parameters():
    global _proxy_parameters_initialized
    global _proxy_parameters
    if not _proxy_parameters_initialized:
        args = iriusrisk.commandline.get_parsed_args()
        if args.proxy_url:
            protocol = "http" if args.port and args.port == 80 else "https"
            _proxy_parameters = {
                protocol: f"{args.proxy_url}:{args.proxy_port}"
            }

        _proxy_parameters_initialized = True

    return _proxy_parameters


"""Calculate the path of the URL. If the project parameter is included, it will 
be URL encoded.
"""
def _build_path(path=(), encode_path=True):
    if type(path) is str:
        path = path.split("/")

    elements = ["api", "v2" ]
    for element in path:
        if encode_path:
            element = urllib.parse.quote(element)

        elements.append(element)

    final_path = "/".join(elements)
    _log.debug(f"Built path '{final_path}'")

    return final_path


def get_target_url():
    global _resolved_url
    if not _resolved_url:
        args = iriusrisk.commandline.get_parsed_args()
        protocol = "https" if args.port == 443 else "http"
        if args.domain:
            _resolved_url = f"{protocol}://{args.domain}:{args.port}"
        elif args.subdomain:
            _resolved_url = f"{protocol}://{args.subdomain}.iriusrisk.com:443"
        else:
            raise Exception("Neither domain nor subdomain specified in the command line parameters!")

        _log.info(f"Endpoint destination is {_resolved_url}")

    return _resolved_url


def get_standards_from_instance():
    results = {}
    _get_standards_from_instance(results, 0)

    return results
    

def _get_standards_from_instance(results, page):
    params = f"page={page}"
    r = do_get(("standards"), params=params)
    if (r.status_code != 200):
        raise Exception(f"Error querying system for standards: {r.reason} ({r.status_code})")

    j = r.json()
    for standard in j["_embedded"]["items"]:
        name = standard["name"]
        ref = standard["referenceId"]
        results[ref] = name
   
    if "next" in j["_links"]:
        _get_standards_from_instance(results, page + 1)


def call_endpoint(path, verb, params=None, headers=None, body=None):
    """Call a named endpoint of the IriusRisk API.

    Arguments:
    path            : the endpoint path. May be a collection of strings, each element
                      another call depth. So to call the URL
                      "/api/v1/products/:productid/threats," you would pass three 
                      elements in the collection, ["products", f"{productid}", "threats"]
    verb            : the verb when calling the endpoint, for instance GET, PUT, POST etc
    params          : (optional) any parameters to include on the call
    headers         : (optional) any headers to include on the call
    body            : (optional) the body of a PUT or POST. Use Multipart when sending a multipart POST

    The method returns a tuple containing the HTTP response and data returned as the body
    of the response. The type of the data depends on two things. First, if convert_response
    is False, plain text is returned. Otherwise, it depends on the return type of the 
    API call. If (for instance) the return type is "application/json," then a json object
    is returned.
    """
    config = iriusrisk.commandline.get_parsed_args()

    if headers is None:
        headers = {
            "accept": "*/*",
            "api-token": config.key,
            "content-type": "application/json"
        }       
    else:
        if not "accept" in headers:
            headers['accept'] = "*/*"

        if not "api-token" in headers:
            headers["api-token"] = config.key
    
        if not "content-type" in headers:
            headers["content-type"] = "application/json"

    target_url = get_target_url()
    path = _build_path(path)
    url = f"{target_url}/{path}"

    proxy = _get_proxy_parameters()

    if not body:
        r = requests.request(verb, url, params=params, headers=headers, proxies=proxy)
    elif isinstance(body, Multipart): 
        # assuption currently is that only one object passed at a time. Might have to 
        # look for an iterable in the future
        files = {
            body.name: ("data", body.payload, body.encoding)
        }
        del(headers["content-type"])
        r = requests.request(verb, url, params=params, headers=headers, files=files, proxies=proxy)
    else:
        r = requests.request(verb, url, params=params, headers=headers, data=body, proxies=proxy)

    return r


"""Make a REST API GET call to the indicated IriusRisk instance."""
def do_get(path, params=None, headers=None):
    return call_endpoint(path, "GET", params=params, body=None, headers=headers)


def do_put(path, body, params=None, headers=None):
    return call_endpoint(path, "PUT", params=params, body=body, headers=headers)


def do_post(path, body, params=None, headers=None):
    return call_endpoint(path, "POST", params=params, body=body, headers=headers)


def do_delete(path, params=None, headers=None):
    return call_endpoint(path, "DELETE", params=params, body=None, headers=headers)


def escape_text(text):
    if isinstance(text, str):
        text = text.replace("\\", "\\\\")
        text = text.replace("\t", "\\t")
        text = text.replace("\n", "\\n")
    elif text:
        # assuming that it's iterable (tuple, list, etc) as it's not a string
        result = None
        for i in text:
            t = escape_text(i)
            result = f"{result}\\t{t}" if result else t

        text = result
    else:
        text = ""

    return text


def get_standards_from_file(name):
    standards = {}
    with open(name, encoding="utf-8") as file:
        while True:
            line = file.readline()
            if not line:
                break

            key, value = line.strip().split("\t")
            standards[key] = value
    
    return standards
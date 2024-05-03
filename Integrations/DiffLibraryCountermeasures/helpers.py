import argparse
import http.client
import json
import logging
import textwrap
from urllib.parse import quote

__all__=["initialize", "do_get", "escape_text"]
log = logging.getLogger(__name__)

def initialize():
    parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter, 
                                     description=textwrap.dedent(
"""Compare libraries of two IriusRisk instances, the 'left' and the 'right' instance. The
domain of the two instances is the fully-qualified domain and subdomain (if present) for 
instances to be searched, without protocol or port. So if the URL of the instance being
logged into is https://iriusrisk.example.com/ui#!login, the domain would be:

    iriusrisk.example.com

and nothing else. Details about a particular library can be parsed by passing in its 
reference. If no reference is specified, then an overview of libraries comparing their 
revision numbers will be output."""), epilog=textwrap.dedent(
"""
OUTPUT:
Output can be directed to stdout by passing the arguments '-o - -q'. The minus-sign 
passed to the -o parameter indicates output to stdout, while -q ensures that no 
spurious data is output via logs.

The data is output in CSV (tab delimited) format. The columns output are:

    Library         : The library's reference number
    Risk Pattern    : The risk pattern's reference number
    Countermeasure  : The countermeasure's reference number
    State           : How the countermeasure changed (NEW, REMOVED, CHANGED, IDENTICAL)
    Name            : The name of the countermeasure
    Description     : The countermeasure's description
    References      : URLs to any references included on the countermeasure, if any
    Test Steps      : Steps to test whether the countermeasure has mitigated the threat

Note that no data besides the identification is included for REMOVED countermeasures. In
other words, if a countermeasure no longer exists in the right instance, only the references
for the library, risk pattern and countermeasure are included."""
))

    parser.add_argument("--l_key", help="The API key for the 'left' instance being queried", required=True, metavar="KEY")
    parser.add_argument("--l_domain", help="The domain for the 'left' instance being queried", required=True, metavar="DOMAIN")
    parser.add_argument("--l_port", help="The port number for the 'left' instance; default: 443", default=443, type=int, metavar="NUM")
    parser.add_argument("--r_key", help="The API key for the 'right' instance being queried", required=True, metavar="KEY")
    parser.add_argument("--r_domain", help="The domain for the 'right' instance being queried", required=True, metavar="DOMAIN")
    parser.add_argument("--r_port", help="The port number for the 'right' instance; default: 443", default=443, type=int, metavar="NUM")
    parser.add_argument("-l", "--library", help="The reference of the library to examine", metavar="REF")
    parser.add_argument("-i", "--ignore_identical", help="Do not output contents of unchanged libraries", action="store_true")
    parser.add_argument("-d", "--debug", help="Print extended information to stdout/stderr", action="store_true")
    parser.add_argument("-q", "--quiet", help="Only print error messages to stdout", action="store_true")
    parser.add_argument("-o", "--output", help="Output results to the indicated file; default: 'results.csv'", default="results.csv", metavar="DEST")
    parser.add_argument("--proxy_port", help="The proxy server port; required if --proxy_url specified", type=int, metavar="NUM")
    parser.add_argument("--proxy_url", help="The proxy server URL, if present", metavar="URL")

    global _args
    _args = parser.parse_args()

    return _args
"""Calculate the path of the URL. If the library parameter is included, it will 
be URL encoded.
"""
def get_path(library):
    path = "/api/v1/libraries"
    if library:
        path = f"{path}/{quote(library)}"

    return path

"""Make a REST API GET call to the indicated IriusRisk instance. Program exits if
anything but a 200 is the result. Returned is the resulting JSON object."""
def do_get(key, domain, port, library=None):
    path = get_path(library)

    headers = {
        "api-token": key,
        "accept": "application/json"
    }

    if _args.proxy_url:
        if not _args.proxy_port:
            raise RuntimeError("Proxy URL was specified but not the proxy port")
        
        log.info(f"Connecting to host via proxy at {_args.proxy_url}:{_args.proxy_port}")
        
        conn = http.client.HTTPSConnection(f"{_args.proxy_url}:{_args.proxy_port}")
        conn.set_tunnel(f"{domain}:{port}")
    else:
        conn = http.client.HTTPSConnection(f"{domain}:{port}")

    conn.request("GET", path, None, headers)
    resp = conn.getresponse()

    if resp.status != 200:
        print(f"Error calling {domain} (respoonse: {resp.status})")
        exit(-1)

    data = resp.read().decode("utf-8")
    return json.loads(data)

def escape_text(text):
    if text:
        text = text.replace("\\", "\\\\")
        text = text.replace("\t", "\\t")
        text = text.replace("\n", "\\n")

    return text

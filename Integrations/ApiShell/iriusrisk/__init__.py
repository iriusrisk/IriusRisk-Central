"""This module provides helper methods for parsing the command line and 
loading configuration files. Call --help on the command line to get detailed
information regarding which arguments are expected on the comand line and in
the configuration files.

Besides initial configuration, this module contains the sub-module "facade,"
which itself provides helper methods for calling the IriusRisk API.

The configuration values are contained in an object named "config," which is
imported by default. The base configuration contains raw command line and
configuration file parameters, plus the attribute "url," which contains the
full URL where the API is being accessed.
"""
import iriusrisk.commandline
import iriusrisk.configfile 
import http.client
import json
import logging
import sys

__all__=["get_config", "get_commandline_parser", "do_initialization", "get_connection"]

_config_holder = [ None ]

_log = logging.getLogger('iriusrisk')
_parser = iriusrisk.commandline.get_parser()

def get_connection(path):
    config = get_config()
    if config.proxy_url:
        proxy = f"{config.proxy_url}:{config.proxy_port}"
        conn = http.client.HTTPSConnection(proxy)
        conn.set_tunnel(path)
        _log.info(f"Connecting to {path} via proxy {proxy}")
    else:
        conn = http.client.HTTPSConnection(path)
        _log.info(f"Connecting to {path}")

    return conn

def get_config():
    if not _config_holder[0]:
        raise Exception("Configuration file not initialized. iriusrisk.parse_arguments() must be called first.")
    
    return _config_holder[0]

"""This returns the instance of the argparse class used by this method. Use 
this to add needed command line parameters prior to calling parse_arguments().
"""
def get_commandline_parser():
    return _parser

"""Parse the command line and load in any initialization files.
"""
def do_initialization():
    global _config_holder
    if _config_holder[0]:
        _log.info("iriusrisk.parse_arguments() called multiple times")
        return

    config = _parser.parse_args()
    _config_holder[0] = config
    
    if config.verbose:
        logging.basicConfig(level=logging.DEBUG)
    elif config.quiet:
        logging.basicConfig(level=logging.ERROR)

    _raw_config = iriusrisk.configfile.parse_config()
    
    if not len(sys.argv) > 1 and not _raw_config:
        _parser.print_help()
        exit(-1)

    if not _raw_config:
        _log.info("No configuration file (iriusrisk.ini) found in any of the locations.")
        _log.info("See help (--help) for more information.")
        _raw_config = { "DEFAULT":{}}
    elif "DEFAULT" in _raw_config:
        _log.info("Successfully parsed at least one configuration file")
    else:
        _log.warn("At least one configuration file was read in, but no [DEFAULT] section was found.")
        _log.info("All configurations in the file(s) will therefore be ignored. See help (--help)")
        _log.info("for further information")

    _log.info("Starting configuration initialization")

    config.key = _get_item(_raw_config, config.key, "key", None)
    config.proxy_port = _get_item(_raw_config, config.proxy_port, "proxy_port", None)
    config.proxy_url = _get_item(_raw_config, config.proxy_url, "proxy_url", None)

    if not config.key:
        _log.error("No --key has been specified. Any API call will fail. See help (--help) for more information.")

    if config.dryrun:
        _log.info("Option --dryrun passed on the command line. No HTTP calls will be made.")
    elif config.proxy_url:
        if not config.proxy_port:
            _log.error("Proxy URL was provided without a proxy port number")
            exit(-1)
    elif config.proxy_port:
        _log.error("Proxy port number was provided without a proxy URL")
        exit(-1)

    config.url = _get_url(_raw_config)
    _check_url(config.url)

def _get_url(config_file):
    config = get_config()
    full_url = _get_item(config_file, config.full_url, "full-url", None)
    if full_url:
        _log.info("Using the --full-url option. No URL will be derived from domain or subdomain.")
        return full_url
    
    subdomain = _get_item(config_file, config.subdomain, "subdomain", None)
    if subdomain:
        _log.info("Using the --subdomain option. URL will be derived by appending .iriusrisk.com (SaaS instance).")
        return f"{subdomain}.iriusrisk.com:443"
    
    domain = _get_item(config_file, config.domain, "domain", None)

    if domain:
        _log.info("Using the --domain option. Protocol assumed to be HTTPS")
        return "{domain}:443"

def _get_item(config_file, value, key, default_value):
    if value:
        _log.debug(f"Found {key} on the command line. Will take precedence over config file")
        return value
    
    if key in config_file["DEFAULT"]:
        _log.debug(f"Found {key} in a configuration file but not on the command line.")
        return config_file["DEFAULT"][key]
    
    _log.debug(f"Item {key} not found in configuration file or on the command line.")
    return default_value

def _check_url(url):
    if not url:
        _log.error("No URL has been specified!")
        _log.warn("You must supply one of subdomain, domain or url on the command line or in the ini file")
        _log.warn("Get extended help (--help) from the program for more information")

    config = get_config()

    if not config.dryrun:
        _log.info("Making a call to the given URL as a fail-fast test")
        _log.debug("Note that this does not test the security key's validity, but just whether")
        _log.debug("the URL is valid and accepting requests.")
        headers = { "accept": "application/json" }
        conn = get_connection(url)
        conn.request("GET", "/health", None, headers)
        resp = conn.getresponse()
        if resp.status != 200:
            _log.error(f"Call to {url} returned status of {resp.status} ({resp.reason}); program will exit")
            exit(-1)

        data = resp.read().decode("utf-8")
        json_obj = json.loads(data)
        _log.debug(f"Successfully checked health of {url} (server: {json_obj['company']})")
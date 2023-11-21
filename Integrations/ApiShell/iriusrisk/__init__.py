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

__all__=["config,parse_arguments,get_commandline_parser"]

config = None
parse_args_on_load = True

_log = logging.getLogger('iriusrisk')
_parser = iriusrisk.commandline.get_parser()

"""Call this method before loading any sub-modules of iriusrisk. This then 
prevents the automatic parsing of the configuration files and command line,
which is normally done following initialization of the sub-modules. 
"""
def suppress_parse_args_on_load():
    parse_args_on_load = False

"""This returns the instance of the argparse class used by this method. Use 
this to add needed command line parameters prior to calling parse_arguments().
"""
def get_commandline_parser():
    return _parser

"""Parse the command line arguments, and load in any config files. By default,
this method is called after any sub-module of iriusrisk is initialized.
"""
def parse_arguments():
    global config
    config = _parser.parse_args()
    
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

    if not config.key:
        _log.error("No --key has been specified. Any API call will fail. See help (--help) for more information.")

    if config.dryrun:
        _log.info("Option --dryrun passed on the command line. No HTTP calls will be made.")

    config.url = _get_url(_raw_config)
    _check_url(config.url)

def _get_url(config_file):
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

    if not config.dryrun:
        _log.info("Making a call to the given URL as a fail-fast test")
        _log.debug("Note that this does not test the security key's validity, but just whether")
        _log.debug("the URL is valid and accepting requests.")
        headers = { "accept": "application/json" }
        conn = http.client.HTTPSConnection(url)
        conn.request("GET", "/health", None, headers)
        resp = conn.getresponse()
        if resp.status != 200:
            _log.error(f"Call to {url} returned status of {resp.status} ({resp.reason}); program will exit")
            exit(-1)

        data = resp.read().decode("utf-8")
        json_obj = json.loads(data)
        _log.debug(f"Successfully checked health of {url} (server: {json_obj['company']})")
import logging
import http.client
import json
import sys

import iriusrisk.v1.commandline as _commandline
import iriusrisk.v1.configfile as _configfile

# Automatically loaded and executed when this module is loaded.
# 
# This script automatically parses the command line and any configuration files found.
# It also determines the ultimate URL that will be used for calling IriusRisk.

__all__=["config", "log"]

class _configuration:
    key = None
    url = None
    verbose = False
    quiet = False
    dryrun = False

config = _configuration()
log = logging.getLogger('iriusrisk.v1')
_parser = _commandline.get_parser()
_parsed_args = ()
_raw_config = _configfile.parse_config()

def _get_item(value, key, default_value=None):
    if value:
        log.debug(f"Found {key} on the command line. Will take precedence over config file")
        return value
    
    if key in _raw_config["DEFAULT"]:
        log.debug(f"Found {key} in a configuration file but not on the command line.")
        return _raw_config["DEFAULT"][key]
    
    log.debug(f"Item {key} not found in configuration file or on the command line.")
    return default_value

def get_url():
    port = _get_item(_parsed_args.port, "port", "443")
    url = _get_item(_parsed_args.url, "url")
    if url:
        log.info("Using the --url option. No URL will be derived from domain or subdomain.")
        return url
    
    subdomain = _get_item(_parsed_args.subdomain, "subdomain")
    if subdomain:
        log.info("Using the --subdomain option. URL will be derived by appending .iriusrisk.com (SaaS instance).")
        return f"{subdomain}.iriusrisk.com:{port}"
    
    domain = _get_item(_parsed_args.domain, "domain")

    if domain:
        log.info("Using the --domain option. Protocol assumed to be HTTPS")
        return "{domain}:{port}"

def check_url(url):
    if not url:
        log.error("No URL has been specified!")
        log.warn("You must supply one of subdomain, domain or url on the command line or in the ini file")
        log.warn("Get extended help (--help) from the program for more information")

    if not config.dryrun:
        log.info("Making a call to the given URL as a fail-fast test")
        log.debug("Note that this does not test the security key's validity, but just whether")
        log.debug("the URL is valid and accepting requests.")
        headers = { "accept": "application/json" }
        conn = http.client.HTTPSConnection(url)
        conn.request("GET", "/health", None, headers)
        resp = conn.getresponse()
        if resp.status != 200:
            log.error("Call to {url} returned status of {resp.status} ({resp.reason}); program will exit")
            exit(-1)

        data = resp.read().decode("utf-8")
        json_obj = json.loads(data)
        log.debug("Successfully checked health of {url} (server: {json_obj['company']})")

### Start reading the config files and command line args
_parser = _commandline.get_parser()

if not len(sys.argv) > 1 and not _raw_config:
    _parser.print_help()
    exit(-1)

_parsed_args = _parser.parse_args()

if _parsed_args.verbose:
    config.verbose = True
    log.setLevel(logging.DEBUG)
elif _parsed_args.quiet:
    config.quiet = True
    log.setLevel(logging.ERROR)

if not _raw_config:
    log.info("No configuration file (iriusrisk.ini) found in any of the locations.")
    log.info("See help (--help) for more information.")
    _raw_config = { "DEFAULT":{}}
elif "DEFAULT" in _raw_config:
    log.info("Successfully parsed at least one configuration file")
else:
    log.warn("At least one configuration file was read in, but no [DEFAULT] section was found.")
    log.info("All configurations in the file(s) will therefore be ignored. See help (--help)")
    log.info("for further information")

log.info("Starting configuration initialization")

config.key = _get_item(_parsed_args.key, "key")

if not config.key:
    log.error("No --key has been specified. Any API call will fail. See help (--help) for more information.")

config.dryrun = _parsed_args.dryrun

if config.dryrun:
    log.info("Option --dryrun passed on the command line. No HTTP calls will be made.")

config.url = get_url()
check_url(config.url)
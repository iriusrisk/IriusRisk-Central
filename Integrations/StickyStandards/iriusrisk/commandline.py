"""This module manages the command line (parameters and parsing) for the current
script. It has several default parameters. A script leveraging this module can
add additional parameters by getting the command line parser (#get_command_line_parser())
prior to intialization.

The arguments retrieved from the command line parse are available by calling
#get_parsed_args(). """
import argparse
import iriusrisk.configfile
import logging
import sys
import textwrap

__all__=["initialize", "do_get", "escape_text", "get_target_url"]

_log = logging.getLogger(__name__)
_command_line_parser = None
_parsed_args = None


"""Returns a list of the parsed arguments from the command line. This may also
include other arguments derived otherwise. The method #initialize() is called
prior to returning the arguments if it hasn't already been called."""
def get_parsed_args():
    if not _parsed_args:
        initialize()

    return _parsed_args


"""Parses the command line."""
def initialize():
    global _parsed_args
    if _parsed_args:
        _log.warning("Calling argument parsing multiple times")
        return _parsed_args
    
    parser = get_command_line_parser()
    _parsed_args = parser.parse_args()

    if _parsed_args.verbose:
        logging.basicConfig(level=logging.DEBUG)
    elif _parsed_args.quiet:
        logging.basicConfig(level=logging.ERROR)

    config = iriusrisk.configfile.parse_config()
    if not len(sys.argv) > 1 and not config:
        _parsed_args.print_help()
        exit(-1)

    if not config:
        _log.info("No configuration file (iriusrisk.ini) found in any of the locations.")
        _log.info("See help (--help) for more information.")
        config = { "DEFAULT":{}}
    elif "DEFAULT" in config:
        _log.info("Successfully parsed at least one configuration file")
    else:
        _log.warn("At least one configuration file was read in, but no [DEFAULT] section was found.")
        _log.info("All configurations in the file(s) will therefore be ignored. See help (--help)")
        _log.info("for further information")

    _log.info("Starting configuration initialization")

    _parsed_args.key = _get_config_value(config, _parsed_args.key, "key", None)
    _parsed_args.port = _get_config_value(config, _parsed_args.port, "port", None)
    _parsed_args.domain = _get_config_value(config, _parsed_args.domain, "domain", None)
    _parsed_args.subdomain = _get_config_value(config, _parsed_args.subdomain, "subdomain", None)
    _parsed_args.proxy_port = _get_config_value(config, _parsed_args.proxy_port, "proxy_port", None)
    _parsed_args.proxy_url = _get_config_value(config, _parsed_args.proxy_url, "proxy_url", None)

    if not _parsed_args.key or not (_parsed_args.subdomain or _parsed_args.domain):
        raise Exception("API key and domain or subdomain need to be specified on the command line (use --help)")
    
    if (_parsed_args.proxy_port is None) != (_parsed_args.proxy_url is None):
        raise Exception("When using a proxy, both the port and URL must be specified")

    return _parsed_args


"""Returns the instance of argparse.ArgumentParser for this instance. This can be altered
to include script-specific command line parameters."""
def get_command_line_parser():
    if _parsed_args:
        _log.warning("Retrieving command line parser after arguments already parsed")

    global _command_line_parser
    if not _command_line_parser:
        _command_line_parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter, 
                                     description=textwrap.dedent(
"""The location of the instance to be queried can be specified in multiple ways. For instance,
you can pass the subdomain for SaaS instances hosted by IriusRisk, or the domain of the
instances without protocol or port.

Some of the command line arguments can appear in configuration files, thereby 
allowing them to be specified across multiple script calls. Configuration files 
are always named "iriusrisk.ini" and are searched for in the following locations:

  * {working directory}/iriusrisk.ini
  * {user data directory}/.iriusrisk/iriusrisk.ini
  * {global data directory}/.iriusrisk/iriusrisk.ini

The same keys may appear in multiple ini files, but the one "nearest" to the
script will be used. For instance, if the same key appears in the ini file
in the working directory and the in the user data directory, the one in the 
working directory takes precedence.

Command line arguments take precedence over ini files."""), epilog=textwrap.dedent(
"""
Note that --subdomain and --domain are mutually exclusive. The --port parameter is optional, 
and is only relevant when using --domain."""
))

        _command_line_parser.add_argument("-k", "--key", help="The API key for the instance being queried", metavar="KEY")
        _command_line_parser.add_argument("-s", "--subdomain", help="The subdomain of the instance being queried", metavar="DOMAIN")
        _command_line_parser.add_argument("-d", "--domain", help="The domain of the instance being queried, without protocol", metavar="DOMAIN")
        _command_line_parser.add_argument("-p", "--port", help="The port number of the instance; default: 443", default=443, type=int, metavar="NUM")
        _command_line_parser.add_argument("-v", "--verbose", help="Print extended information to stdout/stderr", action="store_true")
        _command_line_parser.add_argument("-q", "--quiet", help="Only print error messages to stdout", action="store_true")
        _command_line_parser.add_argument("--proxy_port", help="The proxy server port; required if --proxy_url specified", type=int, metavar="NUM")
        _command_line_parser.add_argument("--proxy_url", help="The proxy server URL, if present", metavar="URL")

    return _command_line_parser


"""The command line works in close conjunction with the configuration file
module. This method checks if a value is in a configuration file and/or on
the command line, preferring the latter if both are present."""
def _get_config_value(config, value, key, default_value):
    if value:
        _log.debug(f"Found {key} on the command line. Will take precedence over config file")
        return value

    if key in config["DEFAULT"]:
        _log.debug(f"Found {key} in a configuration file but not on the command line.")
        return config["DEFAULT"][key]

    _log.debug(f"Item {key} not found in configuration file or on the command line.")
    return default_value
"""This module is deprecated. Use the methods in the iriusrisk.v1 module instead.
"""

import iriusrisk
import logging

_log = logging.getLogger("iriusrisk.v1.facade")

_deprected_do_get_reported = False
_deprected_call_endpoint_reported = False

_log.warning("""Program is using deprecated module iriusrisk.v1.facade. It needs to use the same-named
methods in iriusrisk.v1 instead. Note that loading this module automatically initializes the application
by loading the init files and parsing the command line arguments.
""")

iriusrisk.do_initialization()

def do_get(path, headers={}, params={}, convert_response=True, encode_path=False):
    global _deprected_do_get_reported
    if not _deprected_do_get_reported:
        _log.warning("Calling deprecated method iriusrisk.v1.facade.do_get; call iriusrisk.v1.do_get instead")
        _deprected_do_get_reported = True

    return iriusrisk.v1.do_get(path, headers, params, convert_response, encode_path)

def call_endpoint(path, verb, headers={}, params={}, convert_response=True, encode_path=False):
    global _deprected_call_endpoint_reported
    if not _deprected_call_endpoint_reported:
        _log.warning("Calling deprecated method iriusrisk.v1.facade.call_endpoint; call iriusrisk.v1.call_endpoint instead")
        _deprected_call_endpoint_reported = True

    return iriusrisk.v1.call_endpoint(path, verb, headers, params, convert_response, encode_path)
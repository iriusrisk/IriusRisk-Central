"""This module provides helper methods for accessing IriusRisk API version v1.
It also adds the --key command line parser, which expects the IriusRisk v1 API
key as it's argument.

Specific methods for calling into the API are provided in the iriusrisk.v1.facade
module.
"""
import iriusrisk

iriusrisk.get_commandline_parser().add_argument("-k", "--key", help="API Token to use when accessing the API")
if (iriusrisk.parse_args_on_load):
    iriusrisk.parse_arguments()
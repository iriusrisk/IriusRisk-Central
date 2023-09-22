from iriusrisk.v1 import *

# This import does a few things automatically:
#    * it parses the command line
#    * it attempts to read one or more configuration files
#    * it provides a log variable for logging
#    * all configurations from the command line and configuration files are available on the config variable
#
# For further information to the possible parameters, execute this file with the --help parameter

log.warning(f"Accessing IriusRisk via the URL {config.url}")
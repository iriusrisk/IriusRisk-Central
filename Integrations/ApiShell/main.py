import logging
import iriusrisk.v1 # importing this reads initialization files and parses the command line
from iriusrisk import config

logging.getLogger(__name__).warning(f"Accessing IriusRisk via the URL {config.url}")

help(iriusrisk)
help(iriusrisk.v1)
# the following are in the package "iriusrisk_apishell_v1," available from pypy.
# use "python3 -m pip install iriusrisk_apishell_v1" to install the package.
import iriusrisk 
from iriusrisk.v1 import do_get
import logging

iriusrisk.get_commandline_parser().add_argument("-p", "--project", help="Specify the reference ID of the project to analyze", required=True)
iriusrisk.do_initialization()

# for this to work, you need to provide the API key and the URL, either on
# the command line or an init file. For more information on how to do this,
# call:
#
#    python3 -c 'from iriusrisk.v1 import *' --help
#
# This will output a description of the package command line parameters

log = logging.getLogger(__file__)

config = iriusrisk.get_config()

# using encode_path=True in case the project ref contains invalid URL characters
(resp, json) = do_get(("products", config.project, "threats"), encode_path=True)

log.info(f"Getting threats from project {config.project} at {config.url}")

if resp.status != 200:
    log.fatal(f"Got a {resp.status} when calling Threats API at {config.url}")
    exit(-1)

if len(json) == 0:
    log.warning("Project contains no threats--exiting.")
    exit(0)

first_threat = json[0]["useCase"]["threats"][0]

# Getting the UDT (custom fields) of the threats simply by looking at the Threat output.
# All threats will have the UDTs contained in the output whether they contain values
# or not. So it's possible to find out all the UDT references by looking at the first entry.
udt_refs = []
udt_names = ""
if "udts" in first_threat:
    contains_udts = True
    for udt in first_threat["udts"]:
        ref = udt["ref"]
        udt_refs.append(ref)
        udt_names += f"\tCustom field: {ref}"
else:
    contains_udts = False


print (f"Component Ref\tName\tUse Case\tThreat Ref\tName\tState\tOwner\tConfidentiality\tIntegrity\tAvailability\tEase of Exploit\tInherent Risk\tCurrent Risk\tProjected Risk{udt_names}")

# Threats JSON contains a tree of data for a given project:
# - component
#   {component meta data}
#   {use case}
#     - threats
#       {meta data}
#       {risk ratings}
#       - udts

for component in json:
    comp_ref = component["ref"]
    comp_name = component["name"]
    use_case = component["useCase"]
    uc_name = use_case["name"]

    for threat in use_case["threats"]:
        threat_ref = threat["ref"]
        threat_name = threat["name"]
        threat_state = threat["state"]
        threat_owner = threat["owner"]
        risk_rating = threat["riskRating"]
        conf = risk_rating["confidentiality"]
        integrity = risk_rating["integrity"]
        avail = risk_rating["availability"]
        ease = risk_rating["easeOfExploitation"]
        risk_inherent = threat["inherentRisk"]
        risk_current = threat["risk"]
        risk_projected = threat["projectedRisk"]

        udt_values = ""
        if contains_udts:
            udt_value_map = {}
            for udt in threat["udts"]:
                value = udt["value"]
                if not value:
                    value = ""
                udt_value_map[udt["ref"]] = value

            for udt_ref in udt_refs:
                udt_values = f"\t{udt_value_map[udt_ref]}"

    print (f"{comp_ref}\t{comp_name}\t{uc_name}\t{threat_ref}\t{threat_name}\t{threat_state}\t{threat_owner}\t{conf}\t{integrity}\t{avail}\t{ease}\t{risk_inherent}\t{risk_current}\t{risk_projected}{udt_values}")

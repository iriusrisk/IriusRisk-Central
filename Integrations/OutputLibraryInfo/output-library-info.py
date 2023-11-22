# This script dumps all library information from an IriusRisk instance 
# into an Excel workbook named library_info.xlsx. The workbook contains
# three worksheets:
#
#   Threats: Contains all threats from the libraries
#      Columns: library reference, risk pattern name, use-case, threat name
#   Countermeasures: Contains all countermeasures
#      Cols: library ref, risk pattern name, cm name, cm description
#   Components: Contains all components
#      Cols: component name, comp ref, library ref, risk pattern, countermeasure name
#
# Note: this library uses two modules from PyPi, XlsxWriter and iriusrisk_apishell_v1.
# The IriusRisk library automatically parses the command line, and looks for 
# initialization files in the local file system. From these, it determines the API key 
# and the instance URL. For more information, call:
#
#    python3 -c 'from iriusrisk.v1 import *' --help
#
from iriusrisk import config
from iriusrisk.v1.facade import do_get

import datetime
import logging
import time
import xlsxwriter

start_time = time.time()
log = logging.getLogger(__file__)

(resp, json) = do_get("libraries")

if resp.status != 200:
    log.fatal(f"Call to libraries API returned status code {resp.status}")
    exit(-1)

#############
# Set up the workbook, but only if initial GET to IriusRisk succeeded
workbook = xlsxwriter.Workbook("library_info.xlsx")
ws_threats = workbook.add_worksheet("Threats")
ws_countermeasures = workbook.add_worksheet("Countermeasures")
ws_components = workbook.add_worksheet("Components")

# Add a bold format to use to highlight cells.
bold = workbook.add_format({'bold': True})
    
# Write some data headers.
ws_threats.write('A1', 'Library', bold)
ws_threats.write('B1', 'Risk Pattern', bold)
ws_threats.write('C1', 'Use Case', bold)
ws_threats.write('D1', 'Threat', bold)

ws_countermeasures.write('A1', 'Library', bold)
ws_countermeasures.write('B1', 'Risk Pattern', bold)
ws_countermeasures.write('C1', 'Name', bold)
ws_countermeasures.write('D1', 'Description', bold)

ws_components.write('A1', 'Component Name', bold)
ws_components.write('B1', 'Component Ref', bold)
ws_components.write('C1', 'Library', bold)
ws_components.write('D1', 'Risk Pattern', bold)
ws_components.write('E1', 'Countermeasure', bold)


#############
# indexes for the workbook rows
row_threats = 1
row_cms = 1
row_comps = 1

#############
# mapping to determine countermeasures given a risk pattern, since components
# only map to risk patterns
rp_to_threat = {}
threat_to_cm = {}

stats = {
    "libraries": 0, 
    "components": 0,
    "threats": 0,
    "countermeasures": 0
}

# now loop through all libraries, getting their contents one after another
for library in json:
    stats["libraries"] += 1

    (resp2, json2) = do_get(("libraries", library["ref"]), encode_path=True) # need to encode, since lib ref can contain non-URL tokens
    if resp2.status != 200:
        log.error(f"Failed to get library {json['name']} (ref: {json['ref']})--continuing to next")
        continue

    lib_ref = json2["ref"]
    log.info(f"Succesfully queried library {json2['name']} (ref: {lib_ref})")

    for risk_pattern in json2["riskPatterns"]:
        rp_name = risk_pattern["name"]
        rp_ref = risk_pattern["ref"]
        log.debug(f"..processing risk pattern {rp_name}")

        for use_case in risk_pattern["usecases"]:
            uc_name = use_case["name"]
            log.debug(f"....processing use case {uc_name}")

            for threat in use_case["threats"]:
                stats["threats"] += 1

                ws_threats.write(row_threats, 0, lib_ref)
                ws_threats.write(row_threats, 1, rp_name)
                ws_threats.write(row_threats, 2, uc_name)
                ws_threats.write(row_threats, 3, threat["name"])

                row_threats += 1

                if rp_ref in rp_to_threat:
                    rp_to_threat[rp_ref].append(threat["ref"])
                else:
                    rp_to_threat[rp_ref] = [threat["ref"]]

        log.debug("..processing countermeasures")
        for countermeasure in risk_pattern["countermeasures"]:
            stats["countermeasures"] += 1

            cm_name = countermeasure["name"]
            ws_countermeasures.write(row_cms, 0, lib_ref)
            ws_countermeasures.write(row_cms, 1, rp_name)
            ws_countermeasures.write(row_cms, 2, cm_name)
            ws_countermeasures.write(row_cms, 3, countermeasure["desc"])

            row_cms += 1

            for threat in countermeasure["threats"]:
                threat_ref = threat["ref"]
                if threat_ref in threat_to_cm:
                    threat_to_cm[threat_ref].append(cm_name)
                else:
                    threat_to_cm[threat_ref] = [cm_name]

(resp, json) = do_get("security-content/components")

if resp.status != 200:
    log.error(f"Call to components API returned status code {resp.status}")
else:
    log.info(f"Succesfully queried for all components")
    for component in json:
        stats["components"] += 1

        ref = component["ref"]
        name = component["name"]

        no_cm = True
        for risk_pattern in component["riskPatterns"]:
            rp_ref = risk_pattern["ref"]
            lib_ref = risk_pattern["libraryRef"]
            if rp_ref in rp_to_threat:
                threats = rp_to_threat[rp_ref]
                for threat in threats:
                    if threat in threat_to_cm:
                        countermeasures = threat_to_cm[threat]
                        for cm in countermeasures:
                            ws_components.write(row_comps, 0, name)
                            ws_components.write(row_comps, 1, ref)
                            ws_components.write(row_comps, 2, lib_ref)
                            ws_components.write(row_comps, 3, rp_ref)
                            ws_components.write(row_comps, 4, cm)

                            no_cm = False

                            row_comps += 1

        if no_cm:
            ws_components.write(row_comps, 0, name)
            ws_components.write(row_comps, 1, ref)
            ws_components.write(row_comps, 2, "{no countermeasure associated}")
            row_comps += 1

workbook.close()

end_time = time.time()
elapsed_time = end_time - start_time
pretty_time = str(datetime.timedelta(seconds=elapsed_time))

log.warning(f"""Finished processing all libraries! Here's some info:
  - Output to file            : library_info.xlsx
  - Number of libraries       : {stats['libraries']}
  - Number of threats         : {stats['threats']}
  - Number of countermeasures : {stats['countermeasures']}
  - Number of components      : {stats['components']}
  - Elapsed time              : {pretty_time}""")

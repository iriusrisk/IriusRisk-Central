"""Output a mapping of all countermeasures to the components that they affect.
Specifically, this script loops through all components and recursively searches
its assigned risk patterns for any countermeaures. Once found, the following
information is output:

    Component name  Library name    Countermeasure name

These are tab-separated. The common names of the items is output.

The intention is to allow people creating IriusRisk Rules to have a clear 
mapping when attempting to change the status of countermeasures.
"""
import iriusrisk.commandline
from iriusrisk import *
import logging
import time

_log = logging.getLogger(__file__)

class RiskPattern:
    def __init__(self, uuid, name, library_uuid, library_name):
        self.uuid = uuid
        self.name = name
        self.library_uuid = library_uuid
        self.library_name = library_name

riskpattern_to_countermeasures = {}

"""This method checks the response status of an HTTP call. It 
returns True if a new attempt (or initial attempt) at the call 
should be made, False if the call was successful. The only 
response to return False is 200 (tho theoretically there are
other responses that might justify a False--201, for instance).

The only responses that return True are: no response (i.e., call
has yet to be made) and 503. The 503 can be a temporary situation,
so the method allows for multiple attempts at the call before 
failing.

If a 503 fails too often, and for any other failure statuses,
an exception is raised.
"""
def failover(response, activity_message):
    global wait_time
    if response is None: 
        wait_time = 10
        return True
    
    if response.status_code == 200:
        return False
    
    if response.status_code == 503 and wait_time <= 160:
        _log.info(f"Got a bad gateway error while {activity_message}. Waiting {wait_time} seconds and trying again")
        time.sleep(wait_time)
        wait_time = wait_time * 2
        return True
    
    raise Exception(f"Error {activity_message}: {response.reason} ({response.status_code})")

"""Return all the components in the system. This returns a dicutionary, 
mapping the component UUID to its common name."""
def get_all_components(page=0, components=None):
    if components is None:
        components = {}

    params = f"page={page}"

    r = None
    while failover(r, "getting all components"):
        r = do_get("components", params)
    
    j = r.json()

    for component in j["_embedded"]["items"]:
        components[component["id"]] = component["name"]

    if "next" in j["_links"]:
        get_all_components(page + 1, components)
    else:
        _log.debug(f"  Found a total of {len(components)} components")

    return components

"""Given a component UUID, return a list of all the risk patterns
assigned to it."""
def get_riskpatterns_for_component(uuid, page=0, riskpatterns=None):
    if riskpatterns is None:
        riskpatterns = []

    params = f"page={page}"

    r = None
    while failover(r, "retrieving risk patterns from component"):
        r = do_get(("components", uuid, "risk-patterns"), params)
    
    j = r.json()

    for riskpattern in j["_embedded"]["items"]:
        rp_uuid = riskpattern["id"]
        rp_name = riskpattern["name"]
        library_uuid = riskpattern["library"]["id"]
        library_name = riskpattern["library"]["name"]
        rp = RiskPattern(rp_uuid, rp_name, library_uuid, library_name)
        riskpatterns.append(rp)

    if "next" in j["_links"]:
        get_riskpatterns_for_component(uuid, page + 1, riskpatterns)
    else:
        _log.debug(f"  Found a total of {len(riskpatterns)} risk patterns")

    return riskpatterns

"""Given a risk pattern, get all the countermeasures associated with it. This 
requires multiple recursive calls, given the hiarchical nature of libraries:

Risk pattern
 -> Use Cases
   -> Threats
     -> Weaknesses
       -> Countermeasures

The method decends into the hierarchy to find all the countermeasures. Since
a risk pattern might be referenced by multiple components, risk patterns are
cached. The method first checks if the passed risk pattern was already sought
after. If yes, it returns the cached results. If no, it queries the IriusRisk
instance, caches the results and returns.

The return value is a map of risk pattern UUIDs to a list of countermeasures."""
def get_countermeasures_for_riskpattern(uuid):
    global riskpattern_to_countermeasures
    if uuid in riskpattern_to_countermeasures:
        _log.debug(f"  Countermeasures found for risk pattern {uuid}. Returning from cache.")
        countermeasures = riskpattern_to_countermeasures[uuid]
    else:
        _log.debug(f"  No countermeasures found for {uuid}...")
        countermeasures = find_all_countermeasures_for_riskpattern(uuid)
        riskpattern_to_countermeasures[uuid] = countermeasures

    return countermeasures

"""First step descending the hierarchy is to get all use-cases associated with 
the risk pattern.

Return value is a list of use-cases."""
def get_usecases_from_riskpattern(uuid, page=0, usecases=None):
    if usecases is None:
        usecases = []

    params = f"page={page}"

    r = None
    while failover(r, "getting use-cases from risk pattern"):
        r = do_get(("libraries", "risk-patterns", uuid, "use-cases"), params)

    j = r.json()

    if "_embedded" in j and "items" in j["_embedded"]:
        for usecase in j["_embedded"]["items"]:
            uc_uuid = usecase["id"]
            usecases.append(uc_uuid)
    else:
        _log.debug(f"No usecases returned for riskpattern '{uuid}'")

    if "next" in j["_links"]:
        get_usecases_from_riskpattern(uuid, page + 1, usecases)

    return usecases

"""Each use-case can contain multiple threats. This method returns a list
of threats associated with a particular use-case."""
def get_threats_from_usecase(uuid, page=0, threats=None):
    if threats is None:
        threats = []

    params = f"page={page}"


    r = None
    while failover(r, "getting threats from use-case"):
        r = do_get(("libraries", "use-cases", uuid, "threats", "summary"), params)
    
    j = r.json()
    for threat in j["_embedded"]["items"]:
        threat_uuid = threat["id"]
        threats.append(threat_uuid)

    if "next" in j["_links"]:
        get_threats_from_usecase(uuid, page + 1, threats)

    return threats

"""Finally, given a threat, we can find the associated countermeasures. Note
that we don't have to find weaknesses, since the IriusRisk API returns all
countermeasures for threats, whether they are associated with a weakness or not.

Returned is a dictionary mapping countermeasure UUIDs to common names."""
def get_countermeasures_from_threat(uuid, page=0, countermeasures=None):
    if countermeasures is None:
        countermeasures = {}

    params = f"page={page}"

    r = None
    while failover(r, "getting countermeasures from threat"):
        r = do_get(("libraries", "threats", uuid, "countermeasures"), params)

    j = r.json()
    for countermeasure in j["_embedded"]["items"]:
        cm_uuid = countermeasure["id"]
        cm_name = countermeasure["name"]
        countermeasures[cm_uuid] = cm_name

    if "next" in j["_links"]:
        get_countermeasures_from_threat(uuid, page + 1, countermeasures)

    return countermeasures

"""This method queries IriusRisk recursively to build a list of all
countermeasures associated with a given risk pattern.

Returned is a dictionary mapping countermeasure UUIDs to common names."""
def find_all_countermeasures_for_riskpattern(uuid):
    usecases = get_usecases_from_riskpattern(uuid)
    threats = []
    for usecase in usecases:
        threats = threats + get_threats_from_usecase(usecase, 0, threats)

    countermeasures = {}
    for threat in threats:
        get_countermeasures_from_threat(threat, 0, countermeasures)

    return countermeasures

"""Entry point to the script. It recurisvely discovers all countermeasures
and outputs the results to standard out."""
def main():
    global _args
    _args = iriusrisk.commandline.get_parsed_args()

    components = get_all_components()
    # components = {
    #     "71e174ab-3833-3bf0-9ec6-8e8c068fe581": "Oracle DB"
    # }
    first = True
    for k,v in components.items():
        found_one = False
        _log.info(f"Getting countermeasures for component '{v}'")
        patterns = get_riskpatterns_for_component(k)
        for pattern in patterns:
            _log.debug(f"  Getting countermeasures for pattern '{pattern.name} ({pattern.uuid})'")
            countermeasures = get_countermeasures_for_riskpattern(pattern.uuid)
            for countermeasure in countermeasures.values():
                found_one = True
                if first:
                    first = False
                    print("Component\tLibrary\tCountermeasure")

                print(f"{v}\t{pattern.library_name}\t{countermeasure}")
        if not found_one:
            _log.info(" No countermeasures found.")

if __name__ == "__main__":
    main()
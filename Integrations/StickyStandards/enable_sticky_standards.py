import iriusrisk.commandline
from iriusrisk import *
import logging
import re
import json
import csv
import requests

# Set up logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
_log = logging.getLogger(__file__)

# Command line arguments
iriusrisk.commandline.get_command_line_parser().add_argument(
    "actions",
    metavar="ACTIONS",
    help="Action or actions to perform.  One or both of fields,rules (comma separated).  When creating fields, a custom project field will be added (if it doesn't already exist) for every standard found.  When creating rules, the rules necessary for sticky standards will be created for all the standards found.  These are added to the library 'sticky-standards-autogen,' which is uploaded to IriusRisk.",
)
iriusrisk.commandline.get_command_line_parser().add_argument(
    "-f",
    "--force",
    help="Force an overwrite of library if it exists",
    action="store_true",
)
iriusrisk.commandline.get_command_line_parser().add_argument(
    "-i",
    "--input",
    help="Load the standards from a CSV (tab-delimited) file.  If a file isn't provided, then IriusRisk is queried for all available standards, and rules are created for each.  A list of all standards can be output in CSV format by calling 'python3 output_standards.py.' The results can be edited to include only those standards necessary.",
)

_args = None
_create_udts = False
_create_rules = False


def get_library_id(lib_ref):
    """This queries the instance to get the UUID of the indicated library reference.
    'None' is returned if the library can't be found."""
    params = f"filter='referenceId'='{lib_ref}'"
    try:
        r = do_get(("libraries"), params=params)
        if r.status_code != 200:
            _log.error(
                f"Error querying system for libraries: {r.reason} ({r.status_code}), Response: {r.text}"
            )
            return None, None
    except requests.exceptions.ConnectionError as e:
        _log.error(f"Connection error querying libraries: {e}")
        return None, None

    j = r.json()
    libraries = j["_embedded"]["items"]
    if len(libraries) != 1:
        return None, None

    return libraries[0]["id"], libraries[0]["revision"]


def confirm_overwrite(lib_ver):
    """Confirm with the user that the library should be overwritten. Affirmation is assumed when
    --force is added as a parameter."""
    while True:
        yn = input(
            f"Library 'sticky-standards-autoget' already exists (v{lib_ver}); overwrite? (y/N)> "
        )
        if yn.lower() == "y" or yn.lower() == "yes":
            return
        elif not yn or yn.lower() == "n" or yn.lower() == "no":
            exit(-1)


def get_udt_group_id():
    """All project UDTs for the various standards are collected under the UDT
    group 'Sticky Standards.' If this doesn't already exist, it will be created."""
    params = "filter='name'='Sticky%20Standards'"
    try:
        r = do_get("custom-fields/groups", params)
        if r.status_code != 200:
            _log.error(
                f"Error querying for UDT group: {r.reason} ({r.status_code}), Response: {r.text}"
            )
            raise Exception(
                f"Error querying for UDT group: {r.reason} ({r.status_code})"
            )
    except requests.exceptions.ConnectionError as e:
        _log.error(f"Connection error querying UDT group: {e}")
        raise Exception(f"Connection error: {e}")

    j = r.json()
    if len(j["_embedded"]["items"]) > 0:
        return j["_embedded"]["items"][0]["id"]

    body = """{
  "entity": "project",
  "name": "Sticky Standards"
}"""
    try:
        r = do_post("custom-fields/groups", body)
        if r.status_code != 200:
            _log.error(
                f"Error creating UDT group: {r.reason} ({r.status_code}), Response: {r.text}"
            )
            raise Exception(
                f"Error creating UDT group: {r.reason} ({r.status_code})"
            )
    except requests.exceptions.ConnectionError as e:
        _log.error(f"Connection error creating UDT group: {e}")
        raise Exception(f"Connection error: {e}")

    j = r.json()
    if not "id" in j:
        _log.error(str(j))
        raise Exception(f"Response from server while creating UDT group was malformed")

    return j["id"]


def get_extant_udt_fields(fields=None, page=0):
    """Returns a list of all Project UDT fields."""
    if fields is None:
        fields = {}

    params = f"filter='entity'='project'&page={page}"
    try:
        r = do_get("custom-fields", params)
        if r.status_code != 200:
            _log.error(
                f"Error retrieving current project fields: {r.reason} ({r.status_code}), Response: {r.text}"
            )
            raise Exception(
                f"Error retrieving current project fields: {r.reason} ({r.status_code})"
            )
    except requests.exceptions.ConnectionError as e:
        _log.error(f"Connection error retrieving project fields: {e}")
        raise Exception(f"Connection error: {e}")

    j = r.json()
    for udt in j["_embedded"]["items"]:
        fields[udt["referenceId"]] = udt["id"]

    if "next" in j["_links"]:
        get_extant_udt_fields(fields, page + 1)

    return fields


def get_type_id():
    """The UDT field is of type 'TEXT.' This method returns the UUID associated
    with that field type."""
    params = f"filter='name'='TEXT'"
    try:
        r = do_get(("custom-fields/types"), params=params)
        if r.status_code != 200:
            _log.error(
                f"Error querying system for UDT types: {r.reason} ({r.status_code}), Response: {r.text}"
            )
            raise Exception(
                f"Error querying system for UDT types: {r.reason} ({r.status_code})"
            )
    except requests.exceptions.ConnectionError as e:
        _log.error(f"Connection error querying UDT types: {e}")
        raise Exception(f"Connection error: {e}")

    j = r.json()
    types = j["_embedded"]["items"]
    if len(types) != 1:
        raise Exception("Could not find UDT Type 'TEXT'")

    return types[0]["id"]


def add_udt(group_id, type_id, ref, name):
    """A UDT for the indicated standard wasn't found, so create one."""
    # Construct the JSON payload using json.dumps()
    payload = {
        "entity": "project",
        "name": name,
        "referenceId": ref,
        "typeId": type_id,
        "visible": True,
        "editable": False,
        "exportable": False,
        "groupId": group_id,
    }
    body = json.dumps(payload)
    _log.debug(f"Creating UDT with body: {body}")
    try:
        r = do_post("custom-fields", body)
        if r.status_code != 200:
            _log.error(
                f"Error creating project UDT.  Status code: {r.status_code}, Response: {r.text}"
            )
            raise Exception(
                f"Error creating project UDT: {r.reason} ({r.status_code})"
            )
    except requests.exceptions.ConnectionError as e:
        _log.error(f"Connection error creating UDT: {e}")
        raise Exception(f"Connection error: {e}")

    j = r.json()

    if not "id" in j:
        _log.error(str(j))
        raise Exception(
            f"Response from server while creating project UDT was malformed"
        )

    return j["id"]


def get_udt_fields(standards):
    """Find all Project UDT fields following the Sticky Standards' naming
    convention. This is 'sticky-standard-autogen:{standard-name}."""
    group_id = get_udt_group_id()
    all_fields = get_extant_udt_fields()
    fields = {}
    type_id = None
    for k, v in standards.items():
        ref = f"sticky-standard-autogen:{k}"
        if ref in all_fields:
            fields[ref] = all_fields[ref]
        elif _create_udts:
            if type_id is None:
                type_id = get_type_id()

            id = add_udt(group_id, type_id, ref, v)
            fields[ref] = id

    return fields


def check_actions():
    """Simply confirm that the user included at least one valid action on the
    command line. Valid actions are 'rules' (create and upload library containing
    Rules to automate sticky standards) and 'fields' (create all the Project UDTs
    necessary to implement sticky standards).

    If 'rules' is specified but not 'fields,' then Rules will only be created for
    standards that already have an approrpriate UDT field."""
    a = _args.actions.split(",")
    if len(a) not in (1, 2):
        raise Exception(f"Expected one or two actions, got {len(a)}")

    for action in a:
        if action == "fields":
            global _create_udts
            _create_udts = True
            _log.info("Will create custom project fields")
        elif action == "rules":
            global _create_rules
            _create_rules = True
            _log.info("Will create sticky standards rules")
        elif not action == "output":
            raise Exception(f"Unrecognized action: {action}")


def create_library():
    """Create a library using the API with the appropriate meta-data."""
    body = (
        '{"name": "sticky-standards-autogen","referenceId": "sticky-standards-autogen",'
        '"description": "Auto-generated library for creating sticky standards. DO NOT EDIT!"}'
    )
    try:
        r = do_post("libraries", body)
        if r.status_code != 200:
            _log.error(
                f"Unable to create library sticky-standards-autogen: {r.reason} ({r.status_code}), Response: {r.text}"
            )
            raise Exception(
                f"Unable to create library sticky-standards-autogen: {r.reason} ({r.status_code})"
            )
    except requests.exceptions.ConnectionError as e:
        _log.error(f"Connection error creating library: {e}")
        raise Exception(f"Connection error: {e}")

    j = r.json()
    return j["id"]


def upload_library(id, body):
    """Upload the actual contents of the library once it has been created."""
    if not id:
        id = create_library()

    multipart = Multipart("file", "application/xml", body)

    headers = {"X-Irius-Async": "true"}  # Add the X-Irius-Async header
    try:
        r = do_post(("libraries", id, "update-with-file"), body=multipart, headers=headers)
        if r.status_code != 200:
            data = r.text
            _log.error(f"Error uploading library. Status code: {r.status_code}, Response: {data}")
            raise Exception(
                f"Unable to update library sticky-standards-autogen: {r.reason} ({r.status_code})"
            )
    except requests.exceptions.ConnectionError as e:
        _log.error(f"Connection error uploading library: {e}")
        raise Exception(f"Connection error: {e}")



def get_standards_from_file(filename):
    """
    Reads standards from a CSV file.

    Args:
        filename (str): The name of the CSV file.

    Returns:
        dict: A dictionary of standards, where keys are standard IDs and values are standard names.  Returns empty dict on error.
    """
    standards = {}
    try:
        with open(filename, "r", encoding="utf-8") as csvfile:
            reader = csv.reader(csvfile, delimiter="\t")  # Use tab as delimiter
            header = next(reader)  # Skip the header row
            if not header or len(header) < 2:
                _log.error(
                    f"CSV file '{filename}' is missing required columns (Standard ID and Standard Name)."
                )
                return {}

            for row in reader:
                if len(row) < 2:
                    _log.warning(
                        f"Skipping row in CSV file '{filename}' with insufficient columns: {row}"
                    )
                    continue
                standard_id = row[0].strip()
                standard_name = row[1].strip()
                standards[standard_id] = standard_name
    except FileNotFoundError:
        _log.error(f"CSV file '{filename}' not found.")
        return {}
    except Exception as e:
        _log.error(f"Error reading CSV file '{filename}': {e}")
        return {}
    return standards


def get_standards_from_instance():
    """
    Retrieves all standards from the IriusRisk instance.

    Returns:
        dict: A dictionary of standards, where keys are standard IDs and values are standard names.
    """
    standards = {}
    page = 0
    while True:
        params = f"page={page}"
        try:
            r = do_get("standards", params=params)
            if r.status_code != 200:
                _log.error(
                    f"Error retrieving standards from IriusRisk: {r.reason} ({r.status_code}), Response: {r.text}"
                )
                raise Exception(
                    f"Error retrieving standards from IriusRisk: {r.reason} ({r.status_code})"
                )
        except requests.exceptions.ConnectionError as e:
            _log.error(f"Connection error retrieving standards: {e}")
            raise Exception(f"Connection error: {e}")

        j = r.json()
        for standard in j["_embedded"]["items"]:
            standards[standard["referenceId"]] = standard["name"]

        if "next" not in j["_links"]:
            break
        page += 1
    return standards



TEMPLATE_RULE_PRIMARY = """<?xml version="1.0" encoding="UTF-8"?>
<library ref="sticky-standards-autogen" name="sticky-standards-autogen" enabled="true" revision="@VERSION@" tags="">
  <desc/>
  <categoryComponents/>
  <componentDefinitions/>
  <supportedStandards/>
  <riskPatterns/>
  <rules>
    <rule name="_select-sticky-standards-autogen-q" module="main" generatedByGui="true">
      <conditions/>
      <actions>
        <action project="" value="select-sticky-standards-autogen_::_Sticky Standards_::_Select the standards that should be sticky for this project_::_1_::_false_::_false_::_A sticky standard is one that applies to all components added to this project." name="INSERT_QUESTION_GROUP"/>
      </actions>
    </rule>
    <rule name="_select-sticky-standards-autogen-a" module="main" generatedByGui="true">
      <conditions>
        <condition name="CONDITION_QUESTION_GROUP_EXISTS" field="id" value="select-sticky-standards-autogen_::_group"/>
      </conditions>
      <actions>@ANSWERS@
      </actions>
    </rule>
    @SELECTIONS@
    @ACTIVATIONS@
    @APPLICATIONS@
  </rules>
</library>
"""

TEMPLATE_RULE_ANSWER = """
        <action project="" value="sticky-standard-autogen:@STANDARD_ID@_::_@STANDARD_NAME@_::_" name="INSERT_QUESTION"/>"""

TEMPLATE_RULE_SELECT = """
    <rule name="_select-sticky-standard-autogen-r:@STANDARD_ID@" module="main" generatedByGui="true">
      <conditions>
        <condition name="CONDITION_QUESTION" field="id" value="sticky-standard-autogen:@STANDARD_ID@"/>
      </conditions>
      <actions>
        <action project="" value="ConclusionType.HIDDEN_::_sticky-standard-autogen:@STANDARD_ID@_::_sticky-standard-autogen:@STANDARD_ID@" name="INSERT_CONCLUSION"/>
      </actions>
    </rule>"""

TEMPLATE_RULE_ACTIVATE = """
    <rule name="_activate-sticky-standard-autogen-r:@STANDARD_ID@" module="main" generatedByGui="true">
      <conditions>
        <condition name="CONDITION_CONCLUSION_EXISTS" field="id" value="sticky-standard-autogen:@STANDARD_ID@"/>
      </conditions>
      <actions>
        <action project="" value="sticky-standard-autogen:@STANDARD_ID@_::_Active_::_vsticky_standard_autogen_@V_NAME@" name="UPDATE_UDT"/>
      </actions>
    </rule>
    <rule name="_deactivate-sticky-standard-autogen-r:@STANDARD_ID@" module="main" generatedByGui="true">
      <conditions>
        <condition name="CONDITION_CONCLUSION_NOT_EXISTS" field="id" value="sticky-standard-autogen:@STANDARD_ID@"/>
      </conditions>
      <actions>
        <action project="" value="sticky-standard-autogen:@STANDARD_ID@_::_Inactive_::_vsticky_standard_autogen_@V_NAME@" name="UPDATE_UDT"/>
      </actions>
    </rule>"""

TEMPLATE_RULE_APPLY = """
    <rule name="_apply-sticky-standard-autogen-r:@STANDARD_ID@" module="component" generatedByGui="true">
      <conditions>
        <condition name="CONDITION_USER_DEFINED_FIELD" field="$project" value="Project_::_sticky-standard-autogen:@STANDARD_ID@_::_==_::_Active"/>
      </conditions>
      <actions>
        <action project="" value="@STANDARD_NAME@_::_@STANDARD_ID@_::_false" name="APPLY_SECURITY_STANDARD"/>
      </actions>
    </rule>"""


def main():
    global _args
    _args = iriusrisk.commandline.get_parsed_args()
    check_actions()

    if _create_rules:
        lib_id, lib_ver = get_library_id("sticky-standards-autogen")
        _log.debug(f"Library ID: {lib_id}, Library Version: {lib_ver}")

        if lib_id:
            if not _args.force:
                confirm_overwrite(lib_ver)

            lib_ver += 1
        else:
            lib_id = create_library()
            lib_ver = 1
            _log.debug(f"Created new library with ID: {lib_id}")
            if lib_id is None:
                _log.error("Failed to create library.  Exiting.")
                return

    standards = (
        get_standards_from_file(_args.input)
        if _args.input
        else get_standards_from_instance()
    )
    _log.debug(f"Loaded standards: {standards}")

    if _create_udts:
        get_udt_fields(standards)

    if not _create_rules:
        return

    answers = ""
    selections = ""
    activations = ""
    applications = ""

    for standard_id, standard_name in sorted(standards.items()):
        cleaned_id = re.sub(r"\W+", r"_", standard_id.lower())
        answers += TEMPLATE_RULE_ANSWER.replace("@STANDARD_NAME@", standard_name).replace(
            "@STANDARD_ID@", standard_id
        )
        selections += TEMPLATE_RULE_SELECT.replace("@STANDARD_ID@", standard_id)
        activations += TEMPLATE_RULE_ACTIVATE.replace("@STANDARD_ID@", standard_id).replace(
            "@V_NAME@", cleaned_id
        )
        applications += TEMPLATE_RULE_APPLY.replace("@STANDARD_NAME@", standard_name).replace(
            "@STANDARD_ID@", standard_id
        )
        _log.debug(
            f"Generated rule application for standard: {standard_name} (ID: {standard_id})"
        )
        _log.debug(
            "  Rule: CONDITION_USER_DEFINED_FIELD, field=$project, "
            f"value=Project_::_sticky-standard-autogen:{standard_id}_::_==_::_Active"
        )

    results = TEMPLATE_RULE_PRIMARY.replace("@VERSION@", str(lib_ver)).replace(
        "@ANSWERS@", answers
    ).replace("@SELECTIONS@", selections).replace(
        "@ACTIVATIONS@", activations
    ).replace("@APPLICATIONS@", applications)

    _log.debug(f"Uploading library with content: {results}")
    upload_library(lib_id, results)


if __name__ == "__main__":
    main()

"""This script allows for the easy deletion of one or more Project UDTs
needed for implementing sticky standards. It first obtains all associated
UDTs, then confirms the deletion of each with the user."""
import iriusrisk.commandline
from iriusrisk import *
import logging

iriusrisk.commandline.get_command_line_parser().add_argument("-f", "--force", help="Force delete of all sticky standard UDTs", action="store_true")

_log = logging.getLogger(__file__)


"""Asks the user for confirmation for each UDT. This is assumed to be in the
affirmative either if --force was included on the command line, or the user
enters "all" during any confirmation."""
def confirm_delete_udt(udt_ref):
    global _force_delete
    if _force_delete:
        return True
  
    while True:
        yna = input(f"Delete project UDT '{udt_ref}'? (y/N/all)> ")
        if yna.lower() == "y" or yna.lower() == "yes":
            return True
        elif yna.lower() == "all":
            _force_delete = True
            return True
        elif yna == "" or yna.lower() == "n" or yna.lower() == "no":
            return False


"""Find all Project UDT fields following the Sticky Standards' naming
convention. This is "sticky-standard-autogen:{standard-name}."""
def get_sticky_standard_udts(fields = None, page = 0):
    if fields is None:
        fields = {}
    
    params = f"filter='entity'='project'&page={page}"
    r = do_get("custom-fields", params)
    if r.status_code != 200:
        raise Exception(f"Error retrieving current project fields: {r.status} ({r.reason})")

    j = r.json()
    for udt in j["_embedded"]["items"]:
        ref = udt["referenceId"]
        if ref.startswith("sticky-standard-autogen:"):
          id = udt["id"]
          _log.info(f"Added {ref} ({id})")
          fields[ref] = id

    if "next" in j["_links"]:
        get_sticky_standard_udts(fields, page + 1)

    return fields


"""Call out to the API to delete the indicated UDT."""
def delete_udt(ref, id):
    r = do_delete(("custom-fields", id))
    if r.status_code != 200:
        _log.error(f"Error deleting {ref} ({id})")
        _log.error(f"{r.status}: {r.reason}")
        return False
    
    return True


def main():
    global _args
    _args = iriusrisk.commandline.get_parsed_args()

    global _force_delete
    _force_delete = _args.force

    udts = get_sticky_standard_udts()

    for ref,id in udts.items():
        if confirm_delete_udt(ref):
            if delete_udt(ref, id):
                _log.info(f"Successfully deleted UDT '{ref}'")


if __name__ == "__main__":
    main()
import helpers
from enum import Enum
import logging
import sys

log = logging.getLogger(__name__)

custom_fields = []

class State(Enum):
    NEW = 1
    CHANGED = 2
    REMOVED = 3
    IDENTICAL = 4

def initialize():
    global args
    args = helpers.initialize()
    if args.quiet:
        logging.basicConfig(level=logging.ERROR)
    elif args.debug:
        logging.basicConfig(level=logging.DEBUG)

    global outfile
    if args.output == "-":
        outfile = sys.stderr
    else:
        outfile = open(args.output, "w", encoding="utf-8")

#####
# Code for debugging only. Used to determine the characters contained in references
# for risk patterns and countermeasures. Can safely be ignored.
ref_chars = {}
def process_ref(ref):
    if not args.debug:
        return
    
    for c in ref:
        ref_chars[c] = True

def output_ref_chars():
    if not args.debug:
        return
    
    ignore = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    log.info(f"Special characters found in the descriptions (excluding {ignore}):")
    found = False
    for c in ref_chars:
        if not c in ignore:
            found = True
            log.info(f" '{c}'")

    if not found:
        log.info("  {None found}")
# End debug code.
#####

"""Method checks all the libraries of the old (left) IriusRisk instance with 
the new (right) instance, returning a dictionary. The key of the dictionary
is the library reference ID, and the value is one of the following:

    NEW       : The library only exists in the right instance
    REMOVED   : The library only exists in the left instance
    CHANGED   : The library has different revision numbers in the two instances
    IDENTICAL : No changes between the library in the two instances

A library is considered unchanged if its revision number is identical in both 
instances.
"""
def get_differences(args, libSpecified = None):
    json_l = helpers.do_get(args.l_key, args.l_domain, args.l_port)
    json_r = helpers.do_get(args.r_key, args.r_domain, args.r_port)

    revisions = {}

    # First step: go through all the left libraries and note their revision numbers
    log.warning("Getting all libraries and their revisions from the left instance")
    for library in json_l:
        ref = library["ref"]

        if libSpecified and libSpecified != ref:
            continue

        rev = library["revision"]
        revisions[ref] = rev
        log.info(f"Found {ref}:{rev} in left instance")
    
    differences = {}
    found = {}

    # Next, we'll walk through the right libraries
    log.info("Getting all libraries and their revisions from the right instance")
    for library in json_r:
        ref = library["ref"]

        if libSpecified and libSpecified != ref:
            continue

        rev = library["revision"]
        log.info(f"Found {ref}:{rev} in right instance")
        if not ref in revisions:
            # The library wasn't found in the left instance, so it's new
            log.info(f"  Not in the left instance, so it's new")
            differences[ref] = State.NEW
        elif rev != revisions[ref]:
            # The library was found, but its revision is different, so it's changed
            log.info(f"  Different version than in the left instance, so it's changed")
            differences[ref] = State.CHANGED
            found[ref] = True
        elif args.ignore_identical:
            log.info(f"  Identical revision to the left instance, ignoring")
            found[ref] = True
        else:
            log.info(f"  Identical revision to the left instance")
            differences[ref] = State.IDENTICAL
            found[ref] = True


    # Now, walk through all the left libraries and make sure we saw them all in the right
    for ref in revisions:
        if not ref in found:
            # We did not see this library on the right, so it's been removed
            log.info(f"Library {ref} wasn't in the right instance, so it's been removed")
            differences[ref] = State.REMOVED

    return differences

"""Given connection details and a library reference, go through all countermeasures
and note their relevant info."""
def get_lib_cms(key, domain, port, lib_ref):
    json = helpers.do_get(key, domain, port, lib_ref)
    cms = {}
    for rp in json["riskPatterns"]:
        rp_ref = rp['ref']

        process_ref(rp_ref)

        for cm in rp["countermeasures"]:
            cm_ref = cm["ref"]

            process_ref(cm_ref)

            # Countermeasures may appear multiple times in a library under different
            # risk patterns. Therefore, we're only comparing countermeasures if their
            # risk pattern refs and countermeasure refs are the same.
            dict_key = f"{rp_ref}/{cm_ref}"

            log.info(f"Processing countermeasure: {lib_ref}/{dict_key}")

            if dict_key in cms:
                # This means the same countermeasure appeared twice under a risk pattern.
                # Should never happen.
                log.warning(f"Countermeasure ID found multiple times ({lib_ref}: {cm_ref})")
                continue

            name = cm["name"]
            desc = cm["desc"]
            refs = []

            references = cm["references"]
            if references:
                for ref_ref in references:
                    refs.append(ref_ref["url"])

            steps = cm["test"]["steps"]

            # Add the countermeasure data to the dictionary, keyed to its risk pattern and reference
            cm_map = {
                'name': name,
                'desc': desc,
                'refs': sorted(refs),
                'steps': steps
            }

            if "udts" in cm and cm["udts"]:
                udts = {}
                for udt in cm["udts"]:
                    udt_key = f"udt:{udt['ref']}"

                    global custom_fields
                    if not udt_key in custom_fields:
                        custom_fields.append(udt_key)

                    udt_value = udt["value"]
                    udts[udt_key] = udt_value

                cm_map["udts"] = udts

            cms[dict_key] = cm_map

    return cms

"""Check if two countermeasures are equal. They are considered equal if and 
only if the names, descriptions, references, custom fields and steps are 
all identical."""            
def are_equal(old_cm, new_cm):
    if old_cm['name'] != new_cm['name']:
        return False
    
    if old_cm['desc'] != new_cm['desc']:
        return False
    
    if old_cm['refs'] != new_cm['refs']:
        return False
    
    if "udts" in old_cm:
        if not "udts" in new_cm:
            return False
        
        if old_cm["udts"] != new_cm["udts"]:
            return False
    elif "udts" in new_cm:
        return False
    
    return old_cm['steps'] == new_cm['steps']


def main():
    initialize()
    if args.library:
        differences = get_differences(args, args.library)
    else:
        differences = get_differences(args)

    for lib_ref in differences:
        old_lib = {}
        new_lib = {}

        # check if the library exists in the left instance before fetching it
        if differences[lib_ref] != State.NEW:
            old_lib = get_lib_cms(args.l_key, args.l_domain, args.l_port, lib_ref)

        # check if the library exists in the right instance before fetching it
        if differences[lib_ref] != State.REMOVED:
            new_lib = get_lib_cms(args.r_key, args.r_domain, args.r_port, lib_ref)

        found = {}

        custom_headers = ""
        for cf in custom_fields:
            custom_headers = f"{custom_headers}\t{cf}"

        print(f"Library\tRisk Pattern\tCountermeasure\tState\tName\tDescription\tReferences\tTest Steps{custom_headers}", file=outfile)

        # having gotten all details for the two libraries, loop through and output differences
        for combined_ref in old_lib:
            # split the dictionary key into risk pattern and countermeasure references 
            rp_ref, IGNORE, cm_ref = combined_ref.partition("/")

            # countermeasure existed in the left instance but not the right
            if not combined_ref in new_lib:
                log.info(f"CM REMOVED: {lib_ref}: {combined_ref}")

                print(f"{lib_ref}\t{rp_ref}\t{cm_ref}\tREMOVED\t\t\t\t", file=outfile)
                continue

            found[combined_ref] = True
            old_cm = old_lib[combined_ref]
            new_cm = new_lib[combined_ref]

            # we only care if there are differences between the two countermeasures.
            cms_equal = are_equal(old_cm, new_cm)

            if cms_equal and args.ignore_identical:
                log.info(f"CM IDENTICAL--IGNORING: {lib_ref}: {combined_ref}")
            else:
                text = "IDENTICAL" if cms_equal else "ALTERED"
                log.info(f"CM {text}: {lib_ref}: {combined_ref}")

                steps = new_cm['steps']
                steps = helpers.escape_text(steps)
                desc = new_cm['desc']
                desc = helpers.escape_text(desc)

                udts = new_cm["udts"] if "udts" in new_cm else {}
                
                custom_values = ""

                for udt in custom_fields:
                    val = udts[udt] if udt in udts else ""
                    custom_values = f"{custom_values}\t{val}"

                print(f"{lib_ref}\t{rp_ref}\t{cm_ref}\t{text}\t{new_cm['name']}\t{desc}\t{';'.join(new_cm['refs'])}\t{steps}\t{custom_values}", file=outfile)

        # Now, having looped through the left library, loop through the right one and
        # see if it has countermeasures that don't exist in the left.        
        for combined_ref in new_lib:
            if combined_ref in found:
                continue

            rp_ref, IGNORE, cm_ref = combined_ref.partition("/")

            new_cm = new_lib[combined_ref]
            log.info(f"CM NEW: {lib_ref}: {combined_ref}")

            steps = new_cm['steps']
            steps = helpers.escape_text(steps)
            desc = new_cm['desc']
            desc = helpers.escape_text(desc)

            print(f"{lib_ref}\t{rp_ref}\t{cm_ref}\tNEW\t{new_cm['name']}\t{desc}\t{';'.join(new_cm['refs'])}\t{steps}", file=outfile)

    output_ref_chars()  

if __name__ == "__main__":
    main()
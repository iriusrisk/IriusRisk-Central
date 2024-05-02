"""Output all standards currently associated with the indicated IriusRisk instance.
This list can then be used in conjunction with the enable_sticky_standards.py 
script to curate exactly which standards should be incorporated.
"""

import iriusrisk.commandline
from iriusrisk import *
import sys

iriusrisk.commandline.get_command_line_parser().add_argument("-o", "--output", help="Indicate output file name (default: stdout)", default="-")

_args = None

def main():
    global _args
    _args = iriusrisk.commandline.get_parsed_args()
    if _args.output == "-":
        output = sys.stdout
    else:
        output = open(_args.output, "w", encoding="utf-8")

    standards = get_standards_from_instance()
    for id, name in sorted(standards.items()):
        print(f"{id}\t{name}", file=output)

if __name__ == "__main__":
    main()
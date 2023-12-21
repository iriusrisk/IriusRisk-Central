## Output Threat Details of a Project
The script `output-threat-details.py` takes a project reference and outputs all threats contained
within it in CSV (tab delimited) format. Specifically, it outputs the following details for every 
threat within the project:
* Threat Reference
* Name
* State (Implemented, Required etc)
* Owner
* Risk Rating (Current, Inherent and Projected)
* Values assocaited with all UDTs (custom fields)

### Requirements
* Python 3
* The library [iriusrisk_apishell_v1](https://pypi.org/project/iriusrisk-apishell-v1/)
* A URL to an IriusRisk instance, and
* An [API token](https://support.iriusrisk.com/hc/en-us/articles/360021521291-Get-an-API-Key) associated with the IriusRisk instance

Note that the script is read-only. No changes are made to any IriusRisk project.

### Usage
1. Install the requirements by calling `python3 -m pip install -r requirements.txt` from this (the *./OutputProjectThreats/*) folder.
1. Add the URL and API key to an initialization file. (Alternatively, pass them on the command line using --key and --url.)
1. Call `python3 output-threat-details.py --project {project-ref}`. This will output the CSV results, or any errors encountered.

For further configuration possibilities, or to see how to create an initialization file, call `python3 output-threat-details.py --help`

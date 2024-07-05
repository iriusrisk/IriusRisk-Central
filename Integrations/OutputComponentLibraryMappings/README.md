## OutputComponentLibraryMappings

This program outputs all the mappings in a given system between its components and countermeasures.
In other words, it looks for all the risk patterns associated with a given component, and 
recursively searches for countermeasures in those risk patterns. These mappings are then output
in a CSV (tab-delimited) file, including component name, name of the library containing the 
countermeasure, followed by the name of the countermeasure itself.

The goal of these mappings is to aid IriusRisk admins in the creation of Rules. Specifically,
exactly this information is needed when creating a Rule to set the status of given
countermeasures. This is useful since there is no easy way to work backward from a countermeasure 
in IriusRisk (i.e., find the library and components associated with a particular countermeasure).

### Requirements
* Python 3
* The library [requests](https://pypi.org/project/requests/)
* A URL to an IriusRisk instance, and
* An [API token](https://support.iriusrisk.com/hc/en-us/articles/360021521291-Get-an-API-Key) associated with the IriusRisk instance

### Usage
1. Install the requirements by calling `python3 -m pip install -r requirements.txt` from this (the *./OutputComponentLibraryMappings/*) folder.
1. Specify the URL and API keys (call `python3 main.py --help` for further information)
1. Call `python3 main.py > output.csv`. This will output to standard out the mappings in 
tab-delimited CSV format. 
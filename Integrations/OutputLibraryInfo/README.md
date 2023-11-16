## Output library information
The script `output-library-info.py` extracts information from all the libraries in an IriusRisk instance 
into an Excel workbook. The so-created workbook contains three worksheets:
* **Threats** containing all threats from the libraries, and includes the columns
  * Library reference number
  * Risk pattern name
  * Use-case name, and
  * Threat name
* **Countermeasures** containing all countermeasures in the libraries, with the columns
  * Library reference number
  * Risk pattern name
  * Countermeasure name, and
  * Countermeasure description
* **Components** containing all components from the libraries, mapped to every countermeasure associated with them. It contains the columns
  * Component name
  * Component reference number
  * Library reference number
  * Risk pattern name, and 
  * Countermeasure name

### Requirements
* Python 3
* The libraries [XlsxWriter](https://pypi.org/project/XlsxWriter/) and [iriusrisk_apishell_v1](https://pypi.org/project/iriusrisk-apishell-v1/)
* A URL to an IriusRisk instance, and
* An [API token](https://support.iriusrisk.com/hc/en-us/articles/360021521291-Get-an-API-Key) associated with the IriusRisk instance

The user associated with the API token must have the following global permissions:
* API_ACCESS
* COMPONENT_DEFINITIONS_VIEW
* LIBRARY_VIEW

Note that these permissions are all read-only.

### Usage
1. Install the requirements by calling `python3 -m pip install -r requirements.txt` from this (the *./OutputLibraryInformation/*) folder.
1. Add the URL and API key to an initialization file. (Alternatively, pass them on the command line using --key and --url.)
1. Call `python3 output-library-info.py`. This will generate the file **library_info.xlsx** in the current directory, or will output any errors it encounters.

For further configuration possibilities, call `python3 output-library-info.py --help`

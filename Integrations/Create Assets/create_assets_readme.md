# Purpose

The purpose of this script is to populate sets of assets from a spreadsheet to assist with populating a larger list of assets

# Requirements

Import the following modules - 

1. requests
2. json
3. pandas as pd
4. argparse
5. config (used to import the api key and sub-domain, needs to be in the same directory as the script with the following variables defined.)

    api_key = '{your_api_key}'
sub_domain = '{your_sub_domain}'

# Usage

1. Create a spreadsheet with the following columns - 'name', 'securityClassification_uuid', 'desc'. These correspond to the different payload variables for this api call. 
2. Call the script from the terminal and provide the following arguments 

    python {script_name.py} {spreadsheet location} {spreadsheet_tab_name}

# Results

Successful results will return a 200 code and response of "Asset {name} was created successfully"

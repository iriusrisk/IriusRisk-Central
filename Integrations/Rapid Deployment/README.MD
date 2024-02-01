# Purpose 

The purpose of this set of scripts is to assist with the deployment of the IriusRisk tenant. 

# Requirements

1. Install the underlying requirements

```python

pip3 install -r requirements.txt

```

2. Create a config.py file in the same directory with two values: 

API_KEY = "YOUR API KEY"

URL = "https://yoursubdomain.iriusrisk.com//api/v1"

These could also be imported as environmental variables with some slight adjustments to the script


# Included

The following scripts are included and will each deploy a different area of IriusRisk

## Create Security Classifications

Fill in the required fields on the "Security_class_create" tab on the Rapid_Onboarding.xlsx spreadsheet. 

Those required fields are refID, uuID, name, availability, confidentiality, integrity, and desc. 

This script can be executed in the following manner with the following arguments: 

```python

python3 create_security_classifications.py <location of the spreadsheet> <spreadsheet tab>

```

## Create Trust Zones

Fill in the required fiels on the sheet labeled "trustZones" within the Rapid_Onboardings.xlsx spreadsheet.

Those required fields are name, refID, trustRating, and desc.  

This script can be executed in the following manner with the following arguments:

```python

python3 create_trustzones.py <location of the spreadsheet> <spreadsheet tab>

```

## Create Assets

Fill in the required fiels on the sheet labeled "assets" within the Rapid_Onboardings.xlsx spreadsheet.

Those required fields are name, security classification, securityClassification_UUID, and desc 

This script can be executed in the following manner with the following arguments:

```python

python3 create_assets.py <location of the spreadsheet> <spreadsheet tab>

```



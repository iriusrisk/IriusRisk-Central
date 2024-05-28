# IriusRisk Azure DevOps Integration

This project provides an API-driven approach using Python to integrate Azure DevOps (ADO) as an issue tracker for IriusRisk. There are three main files:

- `config.py`
- `ADOSetup.py`
- `ADO_POST.py`
- `ADO_Sync.py`

## Overview

This project automates the creation of Azure DevOps tickets when certain conditions are met. In this scenario the conditions are when the countermeasure status is 'Required'.
There is also support for passing a custom field value. More details listed below in the optional section.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Configuration](#configuration)
- [Usage](#usage)
- [Optional - Custom Field Configuration](#optional---custom-field-configuration)

## Prerequisites

- Enable the API in IriusRisk settings.
- Obtain a valid IriusRisk API token.
- Ensure the API token is associated with an account with the necessary permissions.
- Ensure you have a valid Azure DevOps project, with a valid subscription and a valid API token.

## Configuration

Update `config.py` with your configuration details.

```python
#----IriusRisk----
domain = 'https://<insert_value>.iriusrisk.com'
sub_url = '/api/v1/products' #initialise
apitoken = '<insert_value>' #IriusRisk API token
head = {'api-token': apitoken}

#----ADO----
organization = "<insert_value>" #ADO org
project = "<insert_value>" #ADO project
personal_access_token = "<insert_value>" #ADO Personal access token
issue_type = "Issue" #set to whatever issue type you are using
```
- domain = insert your IriusRisk tenant name
- apitoken = insert your IriusRisk API token
- organization = insert your Azure DevOps organization name
- project = insert your Azure DevOps project name
- issue_type = insert your Azure DevOps issue type name

## Usage
Once configured, you can run the script to execute the operation, creating new tickets in Azure DevOps (ADO) for all required countermeasures. This will link the new issue back into the project.
Please ensure your IriusRisk project is already configured to Azure DevOps as the Issue Tracker provider if you want the linkage to work as expected. Incorrectly configured projects will correctly create issues, but the linkage will not work.
You may want to schedule this task to run automatically to meet your needs.

## Optional - Custom field configuration

Part of the value in this script is the support for custom field values.

ADOSetup.py
```python
if ADO_CF:
            data.append({
                "op": "add",
                "path": "/fields/Custom.ADO_CF", #set custom field path
                "value": ADO_CF
            })
```
- path = the path to your custom field value in ADO. This will be 'Custom.____' where ____ is the field name, for example 'Custom.MyCustomField'

ADO_Post.py
```python
#ADO_CF = "<Insert_Custom_Field_Value>"
```
- ADO_CF = The value to be passed on item creation for the custom field. Simply uncomment this line and provide a value to pass across. This is currently hard coded but a dynamic option will be coming shortly.



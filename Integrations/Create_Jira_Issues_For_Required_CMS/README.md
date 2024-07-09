# Overview

This project provides an API-driven approach using Python to automatically create issues for all required countermeasures. There are 2 main files:
- `config.py`
- `create_issue_required_cms.py`

## Table of Contents

- [Prerequisites](#prerequisites)
- [Configuration](#configuration)
- [Usage](#usage)

## Prerequisites

- Enable the API in IriusRisk settings.
- Obtain a valid IriusRisk API token.
- Ensure the API token is associated with an account with the necessary permissions.
- Your IriusRisk project has an associated issue tracker profile

## Configuration

Update `config.py` with your configuration details.

```python
#----IriusRisk----
domain = 'https://<Insert_IriusRisk_Tenant_Name>.iriusrisk.com'
sub_url = '/api/v2/projects'
apitoken = '<Insert_API_Token>' #IriusRisk API token
head = {'api-token': apitoken}

# Please insert values for your domain & api token.
```
- domain = insert your IriusRisk tenant name
- apitoken = insert your IriusRisk API token

## Usage
Once configured, you can run the script to execute the operation, creating new tickets for all required countermeasures


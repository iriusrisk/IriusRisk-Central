# Tenant True Up Scripts

This collection of Python scripts is designed to migrate data or configurations from one environment to another.

## Configuration

Before running the scripts, configure your environment settings in `config.py`. 
We need to insert values for the domains & api tokens for both environment, where start is your source domain & post is your target domain.
This file should be set up as follows:

```python
import pip._vendor.requests as requests
import sys
import json

#-------------INITIALISE ENVIRONMENT-----------------#
#set request and head
start_domain = 'https://<insert_domain_name>.iriusrisk.com' # source domain
start_sub_url = '' #initialise
start_apitoken = '<insert_adpi_token>' #insert api token value
start_head = {'api-token': start_apitoken}

post_domain = 'https://<insert_domain_name>.iriusrisk.com' # target domain
post_sub_url = ''
post_apitoken = '<insert_adpi_token>'
post_head = {'api-token': post_apitoken}
```

Important:
Replace 'api-token': '' with your actual API tokens for start_head and post_head to authenticate your API requests.

Usage
To run the scripts, execute the following command from your terminal:


```bash
python script_name.py
```

## Usage notes
We can run scripts in any order, but please make sure to note any dependencies which may dictate the preferential order these are executed.
For example, it would be advised that we run security classification creation before assets, as the assets have a dependency on the security classification
## API Python Module

This module is designed to aid calling the IriusRisk v1 APIs. Use it to create
scripts that create, call and process API calls.

Besides the helper methods this module provides, it also parses the command
line and searches for configuration file entries useful for making IriusRisk
API calls. Most of the command line arguments are also configuration file
entries, thereby allowing default entries that are valid for multiple script
calls.

For further information, install this module locally and run the following:

    python3 -c 'import iriusrisk.autoinit' --help

This describes in greater detail how to call the program shell. 

## Usage example
* Create the file main.py, consisting of the following:

        import iriusrisk.autoinit
        from iriusrisk.v1 import *

        (resp, json) = do_get("products")
        for i in json:
            print(i["name"])

* Call the program from the command line:

        python3 main.py --key {valid API key} --subdomain {SaaS sub-domain}

This will list out the names of all the projects in the specified IriusRisk
instance, available to the user of the API key.

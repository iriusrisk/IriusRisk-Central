## API Shell program

This is a program shell to aid calling IriusRisk APIs. Use this shell to 
create more complex scripts that create, call and process API calls.

Using this shell program provides default command-line and configuration-file
entries useful for making IriusRisk API calls. Most of the command line 
arguments provided can be duplicated in configuration files, thereby allowing
you to provide them in a file once across multiple script calls.

For further information, clone this subdirectory and execute the following:

    python3 -c 'import iriusrisk.auto_initialize' --help

This describes in greater detail how to call the program shell. 

## Usage example
* clone or branch this repository
* Create the file main.py, consisting of the following:

        import iriusrisk.auto_initialize
        from iriusrisk.v1 import *

        (resp, json) = do_get("products")
        for i in json:
            print(i["name"])

* Call the program from the command line:

        cd ./IriusRisk-Central/Integrations/ApiShell/
        python3 main.py --key {valid API key} --subdomain {SaaS sub-domain}

This will list out the names of all the projects in the specified IriusRisk instance, available to the user of the API key.

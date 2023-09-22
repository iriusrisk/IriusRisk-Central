## API Shell program

This is a program shell to aid calling IriusRisk APIs. Use this shell to 
create more complex scripts that create, call and process API calls.

Using this shell program provides default command-line and configuration-file
entries useful for making IriusRisk API calls. Most of the command line 
arguments provided can be duplicated in configuration files, thereby allowing
you to provide them in a file once across multiple script calls.

For further information, clone this subdirectory and execute the main file:

    python3 main.py

This describes in greater detail how to call the program shell. 

### TODO
* Need to look for ini files in multiple locations
* Need to add a toolkit to ease HTTP calls

This will describe in detail how to call the program shell.

## Usage example
* clone or branch this repository
* Edit the main.py file, appending the following lines to it:

        from iriusrisk.v1.facade import call_endpoint

        (resp, json) = call_endpoint("products", "GET")
        for i in json:
            print(i["name"])

* Call the program from the command line:

        cd ./IriusRisk-Central/Integrations/ApiShell/
        python3 main.py --key {valid API key} --subdomain {SaaS sub-domain}

This will list out the names of all the projects in the specified IriusRisk instance, available to the user of the API key.

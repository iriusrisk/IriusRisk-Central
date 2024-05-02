## Integrations
Here you will find anything extending IriusRisk functionality via its APIs. This can include report generation, automated creation or destruction of items, or two-way integrations with third-party tools. Python is a popular scripting language for this, though you may also find Postman scripts, JavaScript or others. 

## Contents
* [Report Generator](Report%20Generator/README.md): This generates a threat report for a product based on its components and associated threats and countermeasures using IriusRisk APIs.
* [OutputLibraryInfo](OutputLibraryInfo/README.md): This outputs the contents of all libraries in a given IriusRisk instance. (It also provides a good example of how to work with the [ApiShell](ApiShell/README.md) module.)
* [ApiShell](ApiShell/README.md): A program shell to aid calling IriusRisk APIs. Use it to create more complex scripts that create, call and process API calls.
* [BU Transfer](bu_transfers/README.md): This script is designed to interact with the IriusRisk API for managing business units, first by getting extant BUs from an instance and next by creating them on another instance.
* Bulk User Import: Assists with the bulk upload of users from a spreadsheet to IriusRisk
* Create Assets: Bulk creates assets within IriusRisk
* Get Aggregate Risk Score: Creates an aggregate risk value from a project and any nested project components
* Get Threats & Countermeasures Report in Excel: Creates an excel output that retrieves threats and countermeasures from a project
* Manage Compoonent Visibility: Manages visibility into full categories of components within the Objects > Components interface 
* Output Project Threats: Outputs threats from a project 
* BU - Transfers: Transfers business units from one tenant to another using the API.
* All Projects Threats Report: Outputs threats from all projects where countermeasures are not in a recommended state into an output json file for import into a secondary tool.
* [StickyStandards](StickyStandards/README.md): Mark standards as being "sticky" at a project level. This causes the indicated standard(s) to be applied to any future changes to the project.

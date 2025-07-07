IR Tool Utility
The IR Tool Utility is designed to facilitate interactions with the IR API, streamlining operations and data management tasks. This document provides instructions on preparing the environment and running the utility.

Prerequisites
Ensure Python3 is installed on your system.

Setup

Clone the repository:
git clone https://github.com/iriusrisk/IriusRisk-Central.git

Preparing the Environment
Before using the IR Tool Utility, you must make the install_irtool_reqs script executable. This script installs the necessary dependencies. Perform the following steps:

Navigate to the directory containing install_irtool_reqs file.

Make the install script executable:
#Command Start
chmod +x "./IriusRisk-Central/Integrations/API Utility/install_irtool_reqs"
#Command End

Run the install script:
#Command Start
"./IriusRisk-Central/Integrations/API Utility/install_irtool_reqs"
#Command End

Copy the ir_api_util folder to your home directory:
#Command Start
cp -r "./IriusRisk-Central/Integrations/API Utility/ir_api_util/" ~
#Command End

Running the Utility
With the environment prepared, you can run the IR Tool Utility from within the cd ir_api_util as follows:

python3 ir_util.py

Follow the on-screen instructions to utilize the utility's features.

Features

Feature: Get Project List (1)
This feature will return a list of the projects in your instance via a JSON file.

Feature: Export IR Project Status (2)
This feature will export the status of your project to CSV and Excel, focusing on countermeasure status. It will prompt you for your IR project reference ID.
In addition, it will include the countermeasure status of associated projects by tag.
For example, if your project contains a project component tagged with the reference ID of its actual project, the countermeasure data for that project component will be included along with the data for your target project.

Feature: Export Project Threat Hierarchy Data (3)
This feature will export the project status, while nesting the project hierachical data with respect to components, use cases, threats, weaknesses and countermeasures.
In addition, the soucre pythong file ("getProject_Threat_Hierarchy_Data.py") includes two toggle options:

 27         # Toggle options
 28         self.include_references =True
 29         self.include_standards = False

These toggles determine whether or not Countermeasure references and standards data are included in the resulting output file.

Feature: User Access Report (8)
This feature generates a report that displays active or inactive users over a specified period in days.

Feature: Business Unit Reports (9)
This feature offers two options. The first option generates a CSV report for a single Business Unit by either Name or UUID. The second option generates the same report for all Business Units.

Feature: Audit Log Report (10)
This feature generates an Excel report focusing on Project Activity and User Activity, sourced from audit log events for up to 180 days.

Feature: API Query Checker (12)
This feature allows users to validate API queries by running checks against expected outputs. It provides two options:

1. Run API Query Checker
   This option executes the API Query Checker to validate queries against sample output files. It checks if the API responses match the expected results.

2. Add New Query to be Checked
   This option allows users to add a new API query for validation. You will be prompted to provide the following details:
   - Friendly Name: A descriptive name for the API query (e.g., "v1 GET Project Details").
   - HTTP Method: The type of request (GET, POST, PUT, DELETE).
   - API URL Endpoint: The API call endpoint (e.g., /v1/projects/{reference-id}).
   - Sample Output File: The path to a JSON file with the expected output.

Once a query is added, it will be included in future checks performed by the API Query Checker.

Feature: Create Trust Zone Policy (13)
This feature allows users to create a drool that targets a trust zone.

1. TZ Policy by Component
   This option creates a Component drool that represetns a Trust Zone Policy that applies to a specific component.

2. TZ Policy by Component Category
   This option creates a Component drool that represents a Trust Zone policy for an entire category of components.

Be sure to name your drool after the policy name you specified.

Additional features may be added as needed in the future...

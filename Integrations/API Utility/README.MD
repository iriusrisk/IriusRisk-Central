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

Copy the ir_api_util folder to you home directory:
#Command Start
cp -r "./IriusRisk-Central/Integrations/API Utility/ir_api_util/" ~
#Command End

Running the Utility
With the environment prepared, you can run the IR Tool Utility as follows:

#Command Start

cd ir_api_util

#Command End

#Command Start

python3 ir_util.py

#Command End

Follow the on-screen instructions to utilize the utility's features.

Features

Feature: Get Project List (1)
Feature Details:
This feature will return via json file, a list of the projects in your instance.


Feature: Export IR Project Status (2)
Feature Details:
This feature will export to CSV and Excel the status of your project with respect to countermeasure status. It will prompt you for you IR project reference ID. 
In addition, it will include the countermeasure status of associated projects by tag.
For example, if your project contains a project component, and you tag that component with reference ID of its actual project, the countermeasure data will for that project component will be included along with the data for your target project.


Feature: User Access Report (8)
Feature Details:
This feature will produce a simple output which diplays the active or inactive users over a given period in days.


Feature: Business Unit Reports
Feature Details:
This feature offers two options. The first option will generate a CSV reports for a single Business Unit by either Name or UUID.
The second option will generate the same reports for all business units.

Additional features to be added as needed in the future.

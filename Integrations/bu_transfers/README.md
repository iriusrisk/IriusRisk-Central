# BU Transfer README

## Overview
This script is designed to interact with the IriusRisk API for managing business units. It performs two main operations:

GET Request: Fetches existing business units from the specified API endpoint.

POST Requests: Creates new business units based on the data retrieved from the GET request.

Prerequisites
Before running the script, ensure you have the following:

Python installed (version 3.x recommended)
Required Python packages: requests
Setup
Clone or download the script to your local machine.

Install the required Python packages:

bash
pip install requests

Create a config.py file with the following variables:

python
Copy code
url_get = "YOUR_GET_API_ENDPOINT"
url_get_api_key = "YOUR_GET_API_KEY"
url_post = "YOUR_POST_API_ENDPOINT"
url_post_api_key = "YOUR_POST_API_KEY"
Replace the placeholder values with your actual API endpoints and keys.

Usage

The script will perform a GET request to fetch existing business units and then iterate through each unit to make POST requests for creating new units.

Important Notes

Ensure that your API endpoints and keys are correctly configured in the config.py file.
The script assumes a successful POST request returns a status code of 201.

Contributing
Feel free to contribute to the script by submitting issues or pull requests.

License
This script is licensed under the MIT License.

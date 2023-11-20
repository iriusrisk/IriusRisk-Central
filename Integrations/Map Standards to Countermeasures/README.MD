# Associated Standards to Countermeasures Script

This script is designed to associate countermeasures with standards in a CMS (Content Management System) using an API. It reads input data from a file (`standards_to_cms.txt`) and makes API requests to associate each countermeasure with the specified standard and reference.

## Requirements

- Python 3.x
- Requests library (`pip install requests`)
- API key for authentication

## Setup

1. Install the required Python packages:

   pip install requests

2. Obtain an API key for authentication and update the `config.py` file with your API key.

## Usage

Create a file named `standards_to_cms.txt` with the following format:

   countermeasure1, standard_ref1, reference1

   countermeasure2, standard_ref2, reference2

   Replace `countermeasure1` (this is a ref ID for the countermeasure), `standard_ref1`, `reference1`, etc., with your actual data.


## Configuration

- Ensure that the `config.py` file contains the correct API key and URL

## Notes

- The script uses the Requests library to make API requests.
- Make sure that your API endpoint and authentication details are correctly configured in the script.
- Check the script's output for any errors or status messages from the API requests.

```

Make sure to replace `script.py` with the actual filename if it's different. Adjust the content based on your specific use case and requirements.

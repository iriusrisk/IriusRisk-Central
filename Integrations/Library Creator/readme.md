# Library Creation Script

This script is designed to automate the creation of security-related entities such as libraries, risk patterns, use cases, threats, weaknesses, and countermeasures in IriusRisk using its API. The script reads input data from a CSV file containing information about these entities and then makes API calls to create them in the IriusRisk platform.

## Prerequisites

Before using this script, ensure that you have the following:

1. **IriusRisk Account**: You must have an account on IriusRisk with the necessary permissions to create libraries, risk patterns, use cases, threats, weaknesses, and countermeasures.

2. **API Key**: Obtain an API key from IriusRisk and replace the placeholder in the `config.py` file with your actual API key.

3. **Python Environment**: Make sure you have Python installed on your machine.

4. **Required Libraries**: Install the required Python libraries by running the following command in your terminal:

   ```python
   pip install -r requirements.txt
   ```

## Configuration

1. Open the `config.py` file and replace the `API_KEY` and `URL` placeholders with your IriusRisk API key and endpoint URL.

```python

API_KEY = "your_api_key"

URL = "your_url_here"

```

## Usage

1. Prepare the input data in a excel file with the following columns:
   - Library
   - Risk_Pattern
   - Use_Case
   - Threat
   - Threat_Desc (this is the description for the threat)
   - Weakness
   - CM (this is the countermeasure)
   - CM_Desc (this is the countermeasure description)
   - standardref (this is the reference id of the standard that already exists in IriusRisk)
   - standardname (this is the name of the standard)
   - supportedstandref (this is the actual reference of the specific standard you are adding)

   Currently it is configured to create ref_ids for each of these elements from the names in the summaries. This could be reconfigured based upon your need for different structures of libraries.

   The script collects those variables from the spreadsheet and inputs those into the function. If you want to add additional variables, they can be collected by a secondary sheet or by adding columns to the existing spreadsheet. An example of this layout has been added to this directory. 

2. Update the script with the correct path to your xlsx file and sheet name. Currently the script is configured to request this information after step three but you can add this directly to the script or the config file with some small modifications.

3. Run the script using the following command:

   ```python
   python library_builder.py
   ```

    It will request the location of the file and the sheet name

    Example:
    ```python

    What is the location of your xlsx spreadsheet? "C:\Users\jrabe_iriusrisk\library_builder\library_contents.xlsx"

    What is the name of the spreadsheet sheet? Library_Creator
    ```

4. The script will iterate through each row of the Excel file, making API calls to create the specified entities in IriusRisk. As it completes each row from the spreadsheet, it will say "Row {counter} complete" to let you know which row of the spreadsheet it has completed.

5. Troubleshooting - Throughout the script are additional output/print statements that print the full resonse.text value to determine why something is failing. This script's focus is on the creation of new content and not on the update of existing content. If the object exists, it will fail and continue on the next API post call. For example, once the first row creates the library, that call will fail for each additional row that gets processed.

## Important Notes

- The script uses the `requests` library to interact with the IriusRisk API.

- Ensure that the entities in your Excel file have unique names or references to avoid conflicts during creation.

- Check the console output for success or error messages after running the script.

- It's recommended to test the script with a small dataset before applying it to a larger set of data.

## Disclaimer

Use this script responsibly and ensure that you have the necessary permissions and approvals before making changes to your IriusRisk environment. The script is provided as-is and may require adjustments based on your specific IriusRisk configuration.

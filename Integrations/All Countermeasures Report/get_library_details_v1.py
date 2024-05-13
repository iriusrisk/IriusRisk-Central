import os
import config
import requests
import get_libraries
import json
import urllib3
from requests.packages.urllib3.exceptions import InsecureRequestWarning
import pandas as pd
from bs4 import BeautifulSoup
import re
from tqdm import tqdm

# Suppress InsecureRequestWarning
urllib3.disable_warnings(InsecureRequestWarning)


def remove_html_tags(text):
    if os.path.isfile(text):  # Check if input is a file
        with open(text, 'r') as file:
            html_content = file.read()
        soup = BeautifulSoup(html_content, "html.parser")
    else:  # Assume input is HTML content
        soup = BeautifulSoup(text, "html.parser")
    clean_text = soup.get_text()
    # Remove illegal characters for Excel
    clean_text = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', clean_text)
    return clean_text



def get_library_details(ref):
    url = f"{config.baseURL}/api/v1/libraries/{ref}"
    headers = {
        'Accept': 'application/json',
        'api-token': config.api_token
    }

    # Disable SSL certificate verification
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        library_data = response.json()

        countermeasures_data = []

        for pattern in library_data.get('riskPatterns', []):
            for countermeasure in pattern.get('countermeasures', []):
                standards = countermeasure.get('standards', [])
                description = remove_html_tags(countermeasure.get('desc', ''))
                countermeasure_data = {
                    'library_ref_id': ref,
                    'countermeasure_ref_id': countermeasure.get('ref', ''),
                    'name': countermeasure.get('name', ''),
                    'description': description,
                    'standards': standards
                }
                countermeasures_data.append(countermeasure_data)

        return countermeasures_data


# Get library names
library_names = get_libraries.get_libraries()

# Aggregate all countermeasure data
all_countermeasures_data = []

print(f''' 
.----------------.  .----------------.  .----------------.  .----------------.  .----------------.  .----------------. 
| .--------------. || .--------------. || .--------------. || .--------------. || .--------------. || .--------------. |
| |  _________   | || |  _________   | || |    _____     | || |              | || |   _______    | || |    ______    | |
| | |  _   _  |  | || | |  _   _  |  | || |   / ___ `.   | || |              | || |  |  ___  |   | || |  .' ____ \   | |
| | |_/ | | \_|  | || | |_/ | | \_|  | || |  |_/___) |   | || |    ______    | || |  |_/  / /    | || |  | |____\_|  | |
| |     | |      | || |     | |      | || |   .'____.'   | || |   |______|   | || |      / /     | || |  | '____`'.  | |
| |    _| |_     | || |    _| |_     | || |  / /____     | || |              | || |     / /      | || |  | (____) |  | |
| |   |_____|    | || |   |_____|    | || |  |_______|   | || |              | || |    /_/       | || |  '.______.'  | |
| |              | || |              | || |              | || |              | || |              | || |              | |
| '--------------' || '--------------' || '--------------' || '--------------' || '--------------' || '--------------' |
 '----------------'  '----------------'  '----------------'  '----------------'  '----------------'  '----------------'

Gathering Countermeasures from Libraries in Tenant {config.baseURL} ... \n\n''')

# Create tqdm progress bar
with tqdm(total=len(library_names), desc="Fetching Countermeasures") as pbar:
    for ref in library_names:
        pbar.set_postfix({"Library": ref})
        countermeasures_data = get_library_details(ref)
        if countermeasures_data:
            all_countermeasures_data.extend(countermeasures_data)
        pbar.update(1)  # Update progress bar

# Export all countermeasure data to a single JSON file
json_filename = "all_countermeasures.json"
with open(json_filename, 'w') as json_file:
    json.dump(all_countermeasures_data, json_file, indent=4)

print(f"All countermeasures exported to {json_filename}")

# Convert JSON data to DataFrame
df = pd.DataFrame(all_countermeasures_data)

# Define column order
columns = ['library_ref_id', 'countermeasure_ref_id', 'name', 'description', 'standards']

# Reorder columns
df = df[columns]

# Export DataFrame to Excel file
excel_filename = "all_countermeasures.xlsx"
df.to_excel(excel_filename, index=False)

print(f"All countermeasures exported to {excel_filename}")

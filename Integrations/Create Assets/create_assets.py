import requests
import json
import pandas as pd
import argparse
import config  # Assuming you have a 'config.py' file with your configuration variables

def asset_creator(name, securityClassification_uuid, desc):
    url = f"https://{config.sub_domain}.iriusrisk.com//api/v2/assets"

    payload = json.dumps({
        "name": name,
        "securityClassification": {
            "id": securityClassification_uuid
        },
        "description": desc
    })
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/hal+json',
        'api-token': f'{config.api_key}'
    }

    response = requests.post(url, headers=headers, data=payload)

    if response.status_code == 200:
        print(f"Asset '{name}' created successfully.")
    else:
        print(f"Failed to create asset '{name}'. Status code: {response.status_code}")
        print(response.text)

def main():
    parser = argparse.ArgumentParser(description='Create assets from a spreadsheet.')
    parser.add_argument('spreadsheet_location', help='Path to the Excel spreadsheet')
    parser.add_argument('sheet_name', help='Name of the sheet in the spreadsheet')
    args = parser.parse_args()

    data = pd.read_excel(args.spreadsheet_location, args.sheet_name)

    for index, row in data.iterrows():
        name = str(row['name'])
        securityClassification_uuid = str(row['securityClassification_uuid'])
        desc = str(row['desc'])

        asset_creator(name, securityClassification_uuid, desc)

if __name__ == '__main__':
    main()

import requests
import json
import pandas as pd
import argparse
import config

def sc_creator(name, availability, confidentiality, integrity, refID, desc):
    url = f"https://{config.sub_domain}.iriusrisk.com//api/v2/security-classifications"

    payload = json.dumps({
        "availability": availability,
        "confidentiality": confidentiality,
        "integrity": integrity,
        "name": name,
        "referenceId": refID,
        "description": desc
    })

    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/hal+json',
        'api-token': f'{config.api_key}'
    }

    response = requests.post(url, headers=headers, data=payload)

    if response.status_code == 200:
        print(f"Security Classification '{name}' created successfully.")
    else:
        print(f"Failed to create security classification '{name}'. Status code: {response.status_code}")
        print(response.text)

def main():
    parser = argparse.ArgumentParser(description='Create security classifications from a spreadsheet.')
    parser.add_argument('spreadsheet_location', help='Path to the Excel spreadsheet')
    parser.add_argument('sheet_name', help='Name of the sheet in the spreadsheet')
    args = parser.parse_args()

    data = pd.read_excel(args.spreadsheet_location, args.sheet_name)

    for index, row in data.iterrows():
        name = str(row['name'])
        refID = str(row['refID'])
        desc = str(row['desc'])
        availability = int(row['availability'])
        confidentiality = int(row['confidentiality'])
        integrity = int(row['integrity'])

        sc_creator(name, availability, confidentiality, integrity, refID, desc)

if __name__ == '__main__':
    main()

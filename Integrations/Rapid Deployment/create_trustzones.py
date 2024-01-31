import requests
import json
import pandas as pd
import argparse
import config  # Assuming you have a 'config.py' file with your configuration variables

def trustzone_creator(name, refID, trustRating, desc):
    url = f"https://{config.sub_domain}.iriusrisk.com//api/v2/trust-zones"

    payload = json.dumps({
        "name": name,
        "referenceId": refID,
        "trustRating": trustRating,
        "description": desc
    })
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/hal+json',
        'api-token': f'{config.api_key}'
    }

    response = requests.post(url, headers=headers, data=payload)

    if response.status_code == 201:
        print(f"Trust zone '{name}' created successfully.")
    else:
        print(f"Failed to create trust zone '{name}'. Status code: {response.status_code}")
        print(response.text)

def main():
    parser = argparse.ArgumentParser(description='Create trust zones from a spreadsheet.')
    parser.add_argument('spreadsheet_location', help='Path to the Excel spreadsheet')
    parser.add_argument('sheet_name', help='Name of the sheet in the spreadsheet')
    args = parser.parse_args()

    data = pd.read_excel(args.spreadsheet_location, args.sheet_name)

    for index, row in data.iterrows():
        name = str(row['name'])
        refID = str(row['refID'])
        trustRating = str(row['trustRating'])
        desc = str(row['desc'])

        trustzone_creator(name, refID, trustRating, desc)

if __name__ == '__main__':
    main()

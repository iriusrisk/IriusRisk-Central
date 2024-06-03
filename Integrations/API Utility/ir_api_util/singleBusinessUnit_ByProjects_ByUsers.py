import os
import sys
import requests
import pandas as pd
import json
from datetime import datetime, timedelta

def read_config(config_path='config.json'):
    try:
        with open(config_path, 'r') as config_file:
            config = json.load(config_file)
            output_path = os.path.expanduser(config.get('output_path', '~/'))
            # Create the directory if it doesn't exist
            os.makedirs(output_path, exist_ok=True)
            return output_path
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error reading config file: {e}. Defaulting to home directory.")
        output_path = os.path.expanduser('~/')
        os.makedirs(output_path, exist_ok=True)
        return output_path

class BaseAPI:
    def __init__(self, api_token_path='~/ir/.ir_user_token', instance_domain_path='~/ir/ir_instance_domain'):
        self.api_token_path = os.path.expanduser(api_token_path)
        self.instance_domain_path = os.path.expanduser(instance_domain_path)
        self.api_token, self.instance_domain = self.read_credentials()
        self.output_path = read_config()

    def read_credentials(self):
        try:
            with open(self.api_token_path, 'r') as token_file:
                api_token = token_file.read().strip()
            with open(self.instance_domain_path, 'r') as domain_file:
                instance_domain = domain_file.read().strip()
            return api_token, instance_domain
        except FileNotFoundError as e:
            print(f"Error: {e}. Make sure the paths are correct.")
            sys.exit(1)

    def make_request(self, endpoint, params={}):
        url = f'https://{self.instance_domain}.iriusrisk.com/api/v2/{endpoint}'
        headers = {
            'Accept': 'application/hal+json',
            'api-token': self.api_token
        }
        try:
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            return response.json()
        except requests.HTTPError as e:
            print(f"HTTP Error: {e.response.status_code} for URL: {e.response.url}")
            return None
        except requests.RequestException as e:
            print(f"Error: {e}")
            return None

class BusinessUnitReport(BaseAPI):
    def __init__(self, api_token_path='~/ir/.ir_user_token', instance_domain_path='~/ir/ir_instance_domain'):
        super().__init__(api_token_path, instance_domain_path)

    def get_business_unit_id(self, business_unit_name_or_uuid):
        business_units_data = self.make_request('business-units?page=0&size=1000')
        if business_units_data is None:
            return None

        for bu in business_units_data.get('_embedded', {}).get('items', []):
            if bu['name'].lower() == business_unit_name_or_uuid.lower() or bu['id'] == business_unit_name_or_uuid:
                return bu['id']
        return None

    def generate_business_unit_project_report(self, business_unit_name_or_uuid):
        business_unit_id = self.get_business_unit_id(business_unit_name_or_uuid)
        if business_unit_id is None:
            print(f"Business Unit '{business_unit_name_or_uuid}' not found.")
            print("")
            return

        projects_data = self.make_request('projects?page=0&size=1000')
        if projects_data is None:
            return

        projects = []
        for project in projects_data.get('_embedded', {}).get('items', []):
            project_id = project['id']
            project_business_units_data = self.make_request(f'projects/{project_id}/ownership/business-units?page=0&size=1000')
            if project_business_units_data is None:
                continue

            business_units = project_business_units_data.get('_embedded', {}).get('items', [])
            for bu in business_units:
                if bu['id'] == business_unit_id:
                    labels = project.get('labels', '')
                    if isinstance(labels, str):
                        tags = labels
                    else:
                        tags = ', '.join(tag['name'] for tag in labels) if labels else ''
                    projects.append({
                        'Business Unit': bu.get('name', ''),
                        'Project(s)': project.get('name', ''),
                        'Reference ID': project.get('referenceId', ''),
                        'Description': project.get('description', ''),
                        'Tags': tags,
                        'Workflow State': project.get('workflowState', {}).get('name', '') if project.get('workflowState') else '',
                        'Owner(s)': ', '.join(owner['username'] for owner in bu.get('owners', [])),
                        'Created Date': project.get('modelUpdated', ''),
                        'Last Edited Date': project.get('modelUpdated', '')
                    })

        df = pd.DataFrame(projects)
        if not df.empty:
            df = df.sort_values(by=['Business Unit', 'Project(s)'])
            csv_file = os.path.join(self.output_path, 'Business_Unit_Project_Report.csv')
            df.to_csv(csv_file, index=False)
            print(f"Business Unit/Project Report saved to {csv_file}")
            print("")
        else:
            print("No data available to generate the Business Unit/Project Report.")
            print("")

    def generate_business_unit_user_listing(self, business_unit_name_or_uuid):
        business_unit_id = self.get_business_unit_id(business_unit_name_or_uuid)
        if business_unit_id is None:
            print(f"Business Unit '{business_unit_name_or_uuid}' not found.")
            print("")
            return

        endpoint = f'business-units/{business_unit_id}/users?page=0&size=1000'
        data = self.make_request(endpoint)
        if data is None:
            return

        users = []
        for item in data.get('_embedded', {}).get('items', []):
            users.append({
                'Business Unit': business_unit_name_or_uuid,
                'Username': item.get('username', ''),
                'Last Name': item.get('lastName', ''),
                'First Name': item.get('firstName', '')
            })

        df = pd.DataFrame(users)
        if not df.empty:
            df = df.sort_values(by=['Business Unit', 'Last Name', 'First Name'])
            csv_file = os.path.join(self.output_path, 'Business_Unit_User_Listing.csv')
            df.to_csv(csv_file, index=False)
            print(f"Business Unit User Listing saved to {csv_file}")
            print("")
        else:
            print("No data available to generate the Business Unit User Listing.")
            print("")

def main():
    if len(sys.argv) != 2:
        print("Usage: python getBusinessUnitReport.py <business_unit_name_or_uuid>")
        sys.exit(1)
    business_unit_name_or_uuid = sys.argv[1]
    report_instance = BusinessUnitReport()
    report_instance.generate_business_unit_project_report(business_unit_name_or_uuid)  # Generate Business Unit/Project Report
    report_instance.generate_business_unit_user_listing(business_unit_name_or_uuid)  # Generate Business Unit User Listing

if __name__ == "__main__":
    main()  # Call main function

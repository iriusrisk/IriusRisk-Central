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
        print("")

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
            print("")

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
            print("")

            return None
        except requests.RequestException as e:
            print(f"Error: {e}")
            print("")

            return None

class BusinessUnitReport(BaseAPI):
    def __init__(self, api_token_path='~/ir/.ir_user_token', instance_domain_path='~/ir/ir_instance_domain'):
        super().__init__(api_token_path, instance_domain_path)

    def get_all_business_units(self):
        business_units_data = self.make_request('business-units?page=0&size=1000')
        if business_units_data is None:
            return []
        return business_units_data.get('_embedded', {}).get('items', [])

    def generate_reports_for_all_business_units(self):
        business_units = self.get_all_business_units()
        if not business_units:
            print("No business units found.")
            print("")

            return

        all_projects = []
        all_users = []

        for bu in business_units:
            business_unit_name = bu.get('name', '')
            business_unit_id = bu.get('id', '')

            # Generate Project Report for Business Unit
            projects_data = self.make_request('projects?page=0&size=1000')
            if projects_data is None:
                continue

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
                        all_projects.append({
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

            # Generate User Listing for Business Unit
            endpoint = f'business-units/{business_unit_id}/users?page=0&size=1000'
            data = self.make_request(endpoint)
            if data is None:
                continue

            for item in data.get('_embedded', {}).get('items', []):
                all_users.append({
                    'Business Unit': business_unit_name,
                    'Username': item.get('username', ''),
                    'Last Name': item.get('lastName', ''),
                    'First Name': item.get('firstName', '')
                })

        # Save Project Report
        project_df = pd.DataFrame(all_projects)
        if not project_df.empty:
            project_df = project_df.sort_values(by=['Business Unit', 'Project(s)'])
            csv_file = os.path.join(self.output_path, 'Business_Unit_Project_Report.csv')
            project_df.to_csv(csv_file, index=False)
            print(f"Business Unit/Project Report saved to {csv_file}")
            print("")
        else:
            print("No data available to generate the Business Unit/Project Report.")
            print("")

        # Save User Listing
        user_df = pd.DataFrame(all_users)
        if not user_df.empty:
            user_df = user_df.sort_values(by=['Business Unit', 'Last Name', 'First Name'])
            csv_file = os.path.join(self.output_path, 'Business_Unit_User_Listing.csv')
            user_df.to_csv(csv_file, index=False)
            print(f"Business Unit User Listing saved to {csv_file}")
            print("")
        else:
            print("No data available to generate the Business Unit User Listing.")
            print("")

def main():
    report_instance = BusinessUnitReport()
    report_instance.generate_reports_for_all_business_units()  # Generate reports for all business units

if __name__ == "__main__":
    main()  # Call main function

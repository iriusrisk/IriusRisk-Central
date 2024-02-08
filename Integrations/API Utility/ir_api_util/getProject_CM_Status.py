import sys
import os
import requests
import pandas as pd

class ProjectComponentStatus:
    def __init__(self, api_token_path='~/ir/.ir_user_token', instance_domain_path='~/ir/ir_instance_domain'):
        self.api_token_path = os.path.expanduser(api_token_path)
        self.instance_domain_path = os.path.expanduser(instance_domain_path)
        self.api_token, self.instance_domain = self.read_credentials()

    def read_credentials(self):
        try:
            with open(self.api_token_path, 'r') as token_file:
                api_token = token_file.read().strip()
            with open(self.instance_domain_path, 'r') as domain_file:
                instance_domain = domain_file.read().strip()
            return api_token, instance_domain
        except FileNotFoundError as e:
            print(f"Error: {e}. Make sure the paths are correct.")
            sys.exit(1)  # Exit if credentials cannot be read

    def fetch_and_export_control_details(self, project_ref):
        df_data = {'Project': [], 'Component': [], 'Control Name': [], 'Control Status': [], 'Priority': []}
        processed_projects = set()  # To avoid processing a project more than once
        self._fetch_project_details(project_ref, df_data, processed_projects)

        # Export to CSV and Excel if data is available
        if df_data['Project']:
            df = pd.DataFrame(df_data)
            csv_file = f'{project_ref}_control_data.csv'
            excel_file = f'{project_ref}_control_data.xlsx'
            df.to_csv(csv_file, index=False)
            df.to_excel(excel_file, index=False)
            print(f"Data exported to {csv_file} and {excel_file}")
        else:
            print("No control data found for the specified project and related projects.")

    def _fetch_project_details(self, project_ref, df_data, processed_projects):
        if project_ref in processed_projects:
            return  # Skip if already processed
        processed_projects.add(project_ref)

        url = f'https://{self.instance_domain}.iriusrisk.com/api/v1/products/{project_ref}'
        try:
            response = requests.get(url, headers={'Accept': 'application/json', 'api-token': self.api_token})
            response.raise_for_status()  # Raises HTTPError for bad responses
            data = response.json()
            components = data.get('components', [])
            for component in components:
                self._process_component(project_ref, component, df_data)
                # Process component tags for referenced projects
                for tag in component.get('tags', []):
                    if tag != project_ref:  # Avoid duplicating the target project
                        self._fetch_project_details(tag, df_data, processed_projects)
        except requests.HTTPError as e:
            print(f"HTTP Error: {e}")
        except requests.RequestException as e:
            print(f"Error fetching project details: {e}")

    def _process_component(self, project_ref, component, df_data):
        controls = component.get('controls', [])
        for control in controls:
            df_data['Project'].append(project_ref)
            df_data['Component'].append(component.get('name', 'No Component'))
            df_data['Control Name'].append(control.get('name', 'No Name'))
            df_data['Control Status'].append(control.get('state', 'No Status'))
            df_data['Priority'].append(control.get('priority', 'No Priority'))

def main(project_ref):
    pcs = ProjectComponentStatus()
    pcs.fetch_and_export_control_details(project_ref)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python getProjectComponentStatus.py <project_ref>")
        sys.exit(1)
    project_ref = sys.argv[1]
    main(project_ref)

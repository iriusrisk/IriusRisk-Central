import sys
import os
import requests
import pandas as pd
import json

def read_config(config_path='config.json'):
    try:
        with open(config_path, 'r') as config_file:
            config = json.load(config_file)
            output_path = os.path.expanduser(config.get('output_path', '~/'))
            os.makedirs(output_path, exist_ok=True)
            return output_path
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error reading config file: {e}. Defaulting to home directory.")
        output_path = os.path.expanduser('~/')
        os.makedirs(output_path, exist_ok=True)
        return output_path

class ProjectComponentStatus:
    def __init__(self, api_token_path='~/ir/.ir_user_token', instance_domain_path='~/ir/ir_instance_domain'):
        self.api_token_path = os.path.expanduser(api_token_path)
        self.instance_domain_path = os.path.expanduser(instance_domain_path)
        self.api_token, self.instance_domain = self.read_credentials()
        self.output_path = read_config()
        
        # Toggle options
        self.include_references = True
        self.include_standards = False

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
    
    def extract_udt_value(self, obj, udt_key):
        for udt in obj.get("udts", []):
            if udt.get("ref") == udt_key:
                return udt.get("value", "")
        return ""

    def fetch_and_export_data(self, project_ref):
        url = f'https://{self.instance_domain}.iriusrisk.com/api/v1/products/{project_ref}'
        try:
            response = requests.get(url, headers={'Accept': 'application/json', 'api-token': self.api_token})
            response.raise_for_status()
            project_data = response.json()
        except requests.RequestException as e:
            print(f"Error fetching project data: {e}")
            return

        df_data = []

        component_controls = {}
        for component in project_data.get("components", []):
            component_controls[component.get("ref", "")] = {ctrl["ref"]: ctrl for ctrl in component.get("controls", [])}

        for component in project_data.get("components", []):
            component_name = component.get("name", "Unknown Component")
            component_ref = component.get("ref", "")

            for usecase in component.get("usecases", []):
                usecase_name = usecase.get("name", "Unknown Use Case")

                for threat in usecase.get("threats", []):
                    threat_name = threat.get("name", "Unknown Threat")
                    threat_ref = threat.get("ref", "")

                    threat_data = {
                        'Project': project_ref,
                        'Component': component_name,
                        'Use case': usecase_name,
                        'Type': 'Threat',
                        'Threat': threat_name,
                        'Threat Ref': threat_ref,
                        'Inherent Risk': threat.get("inherentRisk", ''),
                        'Current Risk': threat.get("risk", ''),
                        'Projected Risk': threat.get("projectedRisk", ''),
                        'Owner': threat.get("owner", ''),
                        'STRIDE-LM': self.extract_udt_value(threat, "SF-T-STRIDE-LM"),
                        'Weakness': '',
                        'Weakness Ref': '',
                        'Countermeasure': '',
                        'Countermeasure Ref': '',
                        'State': '',
                        'Priority': '',
                        'Scope': '',
                        'Standard Baseline': '',
                        'Standard Section': '',
                        'Mitre Reference': '',
                        'Test result': '',
                        'Cost': '',
                        'Reference Name': '',
                        'Reference URL': '',
                        'Standard Name': '',
                        'Standard Ref': ''
                    }
                    df_data.append(threat_data)

                    for weakness in threat.get("weaknesses", []):
                        weakness_data = threat_data.copy()
                        weakness_data.update({
                            'Type': 'Weakness',
                            'Weakness': weakness.get("name", ""),
                            'Weakness Ref': weakness.get("ref", "")
                        })
                        df_data.append(weakness_data)

                    if "controls" in threat and threat["controls"]:
                        for control in threat["controls"]:
                            countermeasure_ref = control.get("ref", "")
                            full_control_data = component_controls.get(component_ref, {}).get(countermeasure_ref, {}) or {}

                            countermeasure_data = threat_data.copy()
                            countermeasure_data.update({
                                'Type': 'Countermeasure',
                                'Countermeasure': full_control_data.get("name", ""),
                                'Countermeasure Ref': countermeasure_ref,
                                'State': full_control_data.get("state", ""),
                                'Priority': full_control_data.get("priority", ""),
                                'Scope': self.extract_udt_value(full_control_data, "SF-C-SCOPE"),
                                'Standard Baseline': self.extract_udt_value(full_control_data, "SF-C-STANDARD-BASELINE"),
                                'Standard Section': self.extract_udt_value(full_control_data, "SF-C-STANDARD-SECTION"),
                                'Mitre Reference': self.extract_udt_value(full_control_data, "SF-C-MITRE"),
                                'Test result': (full_control_data.get("test", {}) or {}).get("source", {}).get("result", ""),
                                'Cost': full_control_data.get("cost", '')
                            })
                            df_data.append(countermeasure_data)
                            
                            if self.include_references:
                                for ref in full_control_data.get("references", []) or []:
                                    reference_data = countermeasure_data.copy()
                                    reference_data.update({
                                        'Type': 'Reference',
                                        'Reference Name': ref.get("name", ""),
                                        'Reference URL': ref.get("url", "")
                                    })
                                    df_data.append(reference_data)
                            
                            if self.include_standards:
                                for std in full_control_data.get("standards", []) or []:
                                    standard_data = countermeasure_data.copy()
                                    standard_data.update({
                                        'Type': 'Standard',
                                        'Standard Name': std.get("name", ""),
                                        'Standard Ref': std.get("ref", "")
                                    })
                                    df_data.append(standard_data)

        df = pd.DataFrame(df_data)
        file_suffix = f"_stnds_{'on' if self.include_standards else 'off'}_refs_{'on' if self.include_references else 'off'}.xlsx"
        excel_file = os.path.join(self.output_path, f'{project_ref}_hierarchical_data{file_suffix}')
        df.to_excel(excel_file, index=False)
        print(f"Data exported to {excel_file}")

def main(project_ref):
    pcs = ProjectComponentStatus()
    pcs.fetch_and_export_data(project_ref)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python getProject_Threat_Hierarchy_Data.py <project_ref>")
        sys.exit(1)
    project_ref = sys.argv[1]
    main(project_ref)

import config
import requests
import get_projects
import json
from datetime import datetime

project_names = get_projects.get_projects()

# Disable SSL certificate verification
requests.packages.urllib3.disable_warnings()


class Threat:
    def __init__(self, ref, name):
        self.ref = ref
        self.name = name


class Control:
    def __init__(self, ref, name, desc, state, priority, risk, threats):
        self.ref = ref
        self.name = name
        self.desc = desc
        self.state = state
        self.priority = priority
        self.risk = risk
        self.threats = []
        if threats is not None:
            self.threats = [Threat(threat['ref'], threat['name']) for threat in threats]


class Component:
    def __init__(self, uuid, ref, name, weaknesses, controls, usecases):
        self.uuid = uuid
        self.ref = ref
        self.name = name
        self.weaknesses = weaknesses
        self.controls = []
        if isinstance(controls, list):
            # If controls is a list, iterate over each control data and initialize Control objects
            self.controls = [
                Control(control['ref'], control['name'], control['desc'], control['state'], control['priority'],
                        control['risk'], control['threats']) for control in controls]
        elif isinstance(controls, dict):
            # If controls is a dictionary, initialize a single Control object
            self.controls = [
                Control(controls['ref'], controls['name'], controls['desc'], controls['state'], controls['priority'],
                        controls['risk'], controls['threats'])]
        else:
            # Handle the case where controls has unexpected data type
            print(f"Invalid controls data format: {controls}")
        self.usecases = usecases


class Project:
    def __init__(self, ref, name, workflowState, assets, trustZones, udts, components):
        self.ref = ref
        self.name = name
        self.workflowState = workflowState
        self.assets = assets
        self.trustZones = trustZones
        self.udts = udts
        self.components = [
            Component(comp['uuid'], comp['ref'], comp['name'], comp['weaknesses'], comp['controls'], comp['usecases'])
            for comp in components]

def qualitative_risk(risk):
    if risk <= 20:
        return "VERY LOW"
    elif risk <= 40:
        return "LOW"
    elif risk <= 60:
        return "MEDIUM"
    elif risk <= 80:
        return "HIGH"
    else:
        return "VERY HIGH"


def get_project_details(ref):
    url = f"{config.baseURL}/api/v1/products/{ref}"
    headers = {
        'Accept': 'application/json',
        'api-token': config.api_token
    }

    # Disable SSL certificate verification
    response = requests.get(url, headers=headers, verify=False)

    if response.status_code == 200:
        project_data = response.json()

        project_output = []
        timestamp = datetime.now()
        timestamp_str = timestamp.strftime("%Y.%m.%d-%H")

        for comp in project_data['components']:
            for control in comp['controls']:
                threats = control.get('threats')
                if threats is not None and control['state'] != "Recommended":
                    for threat in threats:
                        project_output.append({
                            'Project Name': project_data['name'],
                            'Project UDTs': project_data['udts'],
                            'Component Name': comp['name'],
                            'Threat Name': threat['name'],
                            'Threat Risk': control['risk'],
                            'Threat Risk Level': qualitative_risk(control['risk']),
                            'Control Name': control['name'],
                            'Control State': control['state'],
                            'Control Priority': control['priority']
                        })
        # Write to JSON file only if project_output is not empty
        if project_output:
            with open(f'projects_json_output - {timestamp_str}.json', 'a') as f:
                json.dump(project_output, f, indent=4)
                f.write('\n')


for ref in project_names:
    get_project_details(ref)

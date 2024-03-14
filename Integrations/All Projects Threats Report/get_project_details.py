import config
import requests
import get_projects
import json
from datetime import datetime

project_names = get_projects.get_projects()

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
            self.controls = [Control(control['ref'], control['name'], control['desc'], control['state'], control['priority'], control['risk'], control['threats']) for control in controls]
        elif isinstance(controls, dict):
            # If controls is a dictionary, initialize a single Control object
            self.controls = [Control(controls['ref'], controls['name'], controls['desc'], controls['state'], controls['priority'], controls['risk'], controls['threats'])]
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
        self.components = [Component(comp['uuid'], comp['ref'], comp['name'], comp['weaknesses'], comp['controls'], comp['usecases']) for comp in components]

def get_project_details(ref):
    url = f"{config.baseURL}/api/v1/products/{ref}"
    headers = {
        'Accept': 'application/json',
        'api-token': config.api_token
    }

    response = requests.get(url, headers=headers)
    '''
    if response.status_code == 200:
        project_data = response.json()
        formatted_project_data = json.dumps(project_data, indent=4)

        timestamp = datetime.now()
        timestamp_str = timestamp.strftime("%Y-%m-%d %H:%M:%S")

        # Write formatted project data to output.txt file
        with open(f'{ref}.txt', 'w') as f:
            f.write(f"Project Details for reference {ref} Timestamp: {timestamp_str}\n")
            f.write(formatted_project_data + "\n\n")
            f.write("=" * 50 + "\n\n")  # Add separator for each project

        # Create Project instance and print project details
        project = Project(
            project_data['ref'],
            project_data['name'],
            project_data['workflowState'],
            project_data['assets'],
            project_data['trustZones'],
            project_data['udts'],
            project_data['components']
        )
        
        for component in project.components:
            for control in component.controls:
                for threat in control.threats:
                    with open('projects_output.txt', 'a') as f:
                        f.write(f"Project Name - {project.name} // Component Name - {component.name} // Threat Name - {threat.name} // Threat Risk - {control.risk} // Control Name - {control.name} // Control State - {control.state} // Control Priority - {control.priority}  \n\n")

    else:
        print(f"Failed to fetch project details for reference {ref}. Status code: {response.status_code}")
    '''
    if response.status_code == 200:
        project_data = response.json()

        project_output = []
        timestamp = datetime.now()
        timestamp_str = timestamp.strftime("%Y.%m.%d-%H")

        for comp in project_data['components']:
            for control in comp['controls']:
                threats = control.get('threats')  # Get threats
                #if threats is not None and control['state'] != "Recommended":  # Check if threats is not None and control state is not recommended
                if threats is not None:
                    for threat in threats:
                        project_output.append({
                            'Project Name': project_data['name'],
                            'Component Name': comp['name'],
                            'Threat Name': threat['name'],
                            'Threat Risk': control['risk'],
                            'Control Name': control['name'],
                            'Control State': control['state'],
                            'Control Priority': control['priority']
                        })

        with open(f'projects_json_output - {timestamp_str}.json', 'a') as f:
            json.dump(project_output, f, indent=4)
            f.write('\n')

for ref in project_names:
    get_project_details(ref)

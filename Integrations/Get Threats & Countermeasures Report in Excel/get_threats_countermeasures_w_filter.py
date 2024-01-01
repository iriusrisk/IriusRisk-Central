import config
import requests
import json
import argparse
import pandas as pd
from openpyxl import load_workbook

def get_threats(project_ref):
  #remove, used for testing
  #project_ref = "ado-demo"

  url = f"{config.baseURL}/api/v1/products/{project_ref}"

  payload = {}
  headers = {
    'Accept': 'application/json',
    'api-token': config.api_token
  }

  response = requests.get(url, headers=headers, data=payload)

  #print(response.status_code)
  #print(response.json())

  if response.status_code == 200:
    json_data = response.json()

  else:
    print("Woops, something went wrong")

  project_name = json_data["name"]
  workflow_state = json_data["workflowState"]
  trustzones = json_data["trustZones"]
  project_udts = json_data["udts"]

  all_threats = []
  count = 0

  # Access and iterate through components
  components = json_data["components"]
  for index, component in enumerate(components):
    component_name = component["name"]
    component_desc = component["desc"]
    component_group = component["groupName"]
    component_trustZone = component["trustZones"]
    assigned_assets = component["assets"]
    component_library = component["library"]
    component_controls = component["controls"]

    #print(f"Component {index + 1}:")
    #print(f"Name: {component_name}")
    #print(f"Description: {component_desc}")
    #print(f"Group: {component_group}")
    #print(f"Trust Zone: {component_trustZone}")
    #print(f"Assigned Assets: {assigned_assets}")
    #print(f"Library: {component_library}")

    for control in component_controls:
      control_name = control["name"]
      control_state = control["state"]
      control_library = control["library"]
      control_threats = control["threats"]
      control_risk_value = control["risk"]

      for threats in control_threats:
          threat_name = threats['name']
          count +=1
          #uncomment this code-block

          if "Implemented" not in control_state and control_risk_value > 50:
            print(f"Component {component_name} // Threat {count}: {threat_name} // Control: {control_name} // Control Risk - {control_risk_value} // {control_state} - {control_library}")
            print("\n")
          #print(f"Threat {count}: {threat_name} || Control: {control_name} - {control_state} - {control_library}")
          #print("\n")
          all_threats.append({"component_name": component_name, "threat_name": threat_name, "Control":control_name, "Control Risk":control_risk_value, "Control State": control_state})

          df = pd.DataFrame(all_threats)

          df.to_excel("output.xlsx",index=False)



def main():
  parser = argparse.ArgumentParser(description="Retrieve risks and countermeasures associated with project")
  parser.add_argument("project_ref", help="Ref ID of the project")
  #parser.add_argument("workflow_state_filter", help="Ref ID of the workflow state")

  args = parser.parse_args()

  # Call your function with command line arguments
  get_threats(args.project_ref)


if __name__ == "__main__":
  main()
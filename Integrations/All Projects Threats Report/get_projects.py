import requests
import config
import json

def get_projects():
    url = f"{config.baseURL}/api/v1/products"
    headers = {
        'Accept': 'application/json',
        'api-token': config.api_token
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        data = response.json()

        class Project:
            def __init__(self, ref, name, workflowState):
                self.ref = ref
                self.name = name
                self.workflowState = workflowState

        projects = []

        for item in data:
            project = Project(item['ref'], item['name'], item['workflowState'])
            projects.append(project)

        all_project_refs = []

        for project in projects:
            #print('ref:', project.ref)
            all_project_refs.append(project.ref)

        return(all_project_refs)

    else:
        print(f"Failed to fetch projects. Status code: {response.status_code}")

get_projects()

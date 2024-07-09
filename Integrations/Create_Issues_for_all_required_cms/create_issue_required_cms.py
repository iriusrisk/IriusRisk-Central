import requests
import config

def main():
    # Initialization: Construct the base URL and headers for API requests.
    initial_url = config.domain + config.sub_url
    headers = {'api-token': config.apitoken}

    # Fetch projects: Perform a GET request to obtain all projects from the API.
    initial_response = requests.get(initial_url, headers=headers)

    # Check if the projects were retrieved successfully.
    if initial_response.status_code == 200:
        projects = initial_response.json()
        
        # Process each project retrieved from the initial API call.
        for project in projects['_embedded']['items']:
            project_id = project['id']

            # Setup API endpoints specific to the current project.
            query_url = f"{config.domain}/api/v2/projects/{project_id}/countermeasures/query"
            project_settings_url = f"{config.domain}/api/v2/projects/{project_id}/settings"

            # Fetch project settings: Get specific settings for a project.
            settings_response = requests.get(project_settings_url, headers=headers)
            if settings_response.status_code == 200:
                settings = settings_response.json()
                issuetracker_id = settings['issueTrackerProfile']['id']
            
            # Prepare request bodies for querying and posting countermeasures.
            post_body = {
                "countermeasureIds": [],
                "issueTrackerProfileId": issuetracker_id
            }
            query_body = {
                "filters": {
                    "all": {
                        "states": ["required"],
                        "issueStates": ["untracked"]
                    }
                }
            }

            # Query for detailed project data based on specified filters.
            query_response = requests.post(query_url, headers=headers, json=query_body)
            if query_response.status_code == 200:
                query_result = query_response.json()
                cm_ids = [cm['id'] for cm in query_result["_embedded"]["items"]]
            
            # Add countermeasure IDs to the post body if any are found.
            post_body['countermeasureIds'].extend(cm_ids)
            
            # Only proceed with POST request if there are countermeasure IDs to process.
            if post_body['countermeasureIds']:
                post_url = f"{config.domain}{config.sub_url}/{project_id}/countermeasures/create-issues/bulk"
                # Perform a POST request to create issues in bulk for the countermeasures.
                final_response = requests.post(post_url, headers={**headers, 'X-Irius-Async': 'true'}, json=post_body)
                # Check response status from the bulk create operation.
                if final_response.status_code in [200, 201, 202]:
                    print("Post successful")
                else:
                    print(final_response.status_code)
                    print(final_response.text)
                    
    else:
        # Handle failure to retrieve projects with a message including the status code.
        print(f"Failed to retrieve projects. Status Code: {initial_response.status_code}")

if __name__ == "__main__":
    main()

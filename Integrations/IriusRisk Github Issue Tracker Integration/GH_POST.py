import requests
import config
import GHSetup

def main():
    # Initialize the GitHub issue tracker
    issue_tracker = GHSetup.GithubIssueTracker(config.owner, config.repo, config.personal_access_token)

    response = requests.get(config.domain + config.sub_url_api_v2, headers={'api-token': config.apitoken})
    
    #print(response.json())

    
    if response.status_code == 200:
        projects = response.json()
        for project in projects['_embedded']['items']:
            
            #check project CF value
            for cf in project['customFields']:
                if cf['customField']['name'] == "IssueTrackerType":
                    if cf['value'] == "Github":
        
                        project_id = project['id']
                        project_url = f"{config.domain}/api/v2/projects/{project_id}/countermeasures"
                        
                        # Fetch detailed project data
                        response = requests.get(project_url, headers={'api-token': config.apitoken})
                        if response.status_code == 200:
                            countermeasures = response.json()
                            for countermeasure in countermeasures['_embedded']['items']:
                                if countermeasure['state'] == 'required':
                                    countermeasure_id = countermeasure['id']                               
                                    url = f"{config.domain}/api/v2/projects/countermeasures/{countermeasure_id}/references"
                                    
                                    # Fetch detailed reference data for the countermeasure
                                    response = requests.get(url, headers={'api-token': config.apitoken})
                                    references = response.json()
                                    
                                    reference_found = False  # Flag to track if 'Github Issue Link' is found
                                    if response.status_code == 200:
                                        for reference in references['_embedded']['items']:
                                            if reference['name'] == "Github Issue Link":
                                                reference_found = True
                                                break
                                        
                                        if not reference_found:
                                            # Perform the logic to create the link since it doesn't exist
                                            title = f"Countermeasure ref: {countermeasure['referenceId']}"
                                            body = f"Description: {countermeasure['description']}\nState: {countermeasure['state']}"
                                            labels = ["bug"]
                                            
                                            response = issue_tracker.create_issue(title, body, None, None, labels)
                                            if response.status_code == 201:
                                                GH_response = response.json()
                                                new_issue_link = GH_response['html_url']
                                                new_issue_link_api = GH_response['url']
                                                
                                                # PUT new data
                                                sub_url = '/api/v2/projects/countermeasures/references'
                                                url = config.domain + sub_url
                                                
                                                # JSON Body to pass to PUT request
                                                myobjs = [
                                                    {
                                                        "countermeasure": {
                                                            "id": countermeasure_id
                                                        },
                                                        "name": "Github Issue Link",
                                                        "url": new_issue_link
                                                    }, 
                                                    {"countermeasure": {
                                                            "id": countermeasure_id
                                                        },
                                                        "name": "Github Issue Link - API",
                                                        "url": new_issue_link_api
                                                    }
                                                ]
                                                for myobj in myobjs:
                                                    # Send PUT request
                                                    response = requests.post(url, headers={'api-token': config.apitoken}, json=myobj)
                                                    if response.status_code == 201:
                                                        print('Successful post')
                                                    else:
                                                        print(response.text)
                                            else:
                                                print(f"Failed to create issue. Status Code: {response.status_code}")
    else:
        print(f"Failed to retrieve projects. Status Code: {response.status_code}")

if __name__ == "__main__":
    main()
import requests
import config

def extract_core_message(comment):
    """Strip any user context and return the core message."""
    parts = comment.split(' commented: ')
    if len(parts) > 1:
        return parts[1].strip()
    return parts[0].strip()

def update_countermeasure_status(countermeasure, status):
    """Update the status of a countermeasure in IriusRisk."""
    data = {
                "stateTransition": "implemented"
            }
    response = requests.put(f"{config.domain}/api/v2/projects/countermeasures/{countermeasure['id']}/state", headers={'api-token': config.apitoken}, json=data)
    if response.status_code == 200:
        print(f'Countermeasure status updated to {status}')
    else:
        print(f'Failed to update countermeasure status: {response.status_code}, {response.text}, {response.json()}')

def sync_comments():
    # Get projects from IriusRisk
    projects_response = requests.get(config.domain + config.sub_url_api_v2, headers={'api-token': config.apitoken})
    if projects_response.status_code == 200:
        projects = projects_response.json()
        for project in projects['_embedded']['items']:
            for cf in project['customFields']:
                if cf['customField']['name'] == "IssueTrackerType" and cf['value'] == "Github":
                    project_id = project['id']
                    # Get countermeasures for the project
                    countermeasures_response = requests.get(f"{config.domain}/api/v2/projects/{project_id}/countermeasures", headers={'api-token': config.apitoken})
                    if countermeasures_response.status_code == 200:
                        countermeasures = countermeasures_response.json()
                        for countermeasure in countermeasures['_embedded']['items']:
                            if countermeasure['state'] == 'required':
                                countermeasure_id = countermeasure['id']
                                # Get references to find Github API URL
                                references_response = requests.get(f"{config.domain}/api/v2/projects/countermeasures/{countermeasure_id}/references", headers={'api-token': config.apitoken})
                                references = references_response.json()
                                for reference in references['_embedded']['items']:
                                    if reference['name'] == "Github Issue Link - API":
                                        GH_API_url = reference['url']

                                        # Fetch comments from Github
                                        GH_comments_response = requests.get(GH_API_url + '/comments', headers=config.GH_head)
                                        GH_comments = GH_comments_response.json()

                                        # Check if GitHub issue is closed
                                        GH_issue_response = requests.get(GH_API_url, headers=config.GH_head)
                                        GH_issue = GH_issue_response.json()
                                        if GH_issue['state'] == 'closed':
                                            update_countermeasure_status(countermeasure, 'implemented')

                                        # Fetch comments from IriusRisk
                                        IR_comments_response = requests.get(f"{config.domain}/api/v2/projects/countermeasures/{countermeasure_id}/comments", headers={'api-token': config.apitoken})
                                        IR_comments = IR_comments_response.json()

                                        # Prepare comments for sync
                                        GH_comments_dict = {extract_core_message(comm['body']): f"{comm['user']['login']} commented: {comm['body']}" for comm in GH_comments}
                                        IR_comments_dict = {extract_core_message(comm['comment']): f"{comm['user']['username']} commented: {comm['comment']}" for comm in IR_comments['_embedded']['items']}

                                        # Sync from Github to IriusRisk
                                        for core_message, full_message in GH_comments_dict.items():
                                            if core_message not in IR_comments_dict:
                                                print(f"Posting to IriusRisk: '{full_message}'")
                                                post_to_iriusrisk(full_message, countermeasure_id)

                                        # Sync from IriusRisk to Github
                                        for core_message, full_message in IR_comments_dict.items():
                                            if core_message not in GH_comments_dict:
                                                print(f"Posting to Github: '{full_message}'")
                                                post_to_github(full_message, GH_API_url)

def post_to_iriusrisk(comment, countermeasure_id):
    data = {"countermeasure": {"id": countermeasure_id}, "comment": comment}
    response = requests.post(f"{config.domain}/api/v2/projects/countermeasures/comments", headers={'api-token': config.apitoken}, json=data)
    if response.status_code == 200:
        print('Comment added to IriusRisk')

def post_to_github(comment, api_url):
    data = {"body": comment}
    response = requests.post(api_url + '/comments', headers=config.GH_head, json=data)
    if response.status_code == 201:
        print('Comment added to Github')

if __name__ == "__main__":
    sync_comments()

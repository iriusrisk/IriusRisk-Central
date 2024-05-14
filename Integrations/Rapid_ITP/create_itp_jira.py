import requests
import json
import argparse
import config


# Create ArgumentParser object
parser = argparse.ArgumentParser(description='Creates and publishes an issue tracker profile quickly.')

# Add arguments
parser.add_argument('--subDomain', help='Enter the subdomain of your instance')
parser.add_argument('--apiKey', help='Enter the API key for this domain')
parser.add_argument('--jiraUserName', help='Enter your Jira user ID')
parser.add_argument('--jiraKey', help='Enter the JIRA API Key')
parser.add_argument('--projectKey', help='Enter your Jira Project Key')

# Parse the arguments
args = parser.parse_args()

# Access the arguments

# FIRST API CALL TO CREATE THE UNPUBLISHED AND INCOMPLETE ITP

url = f"https://{args.subDomain}.iriusrisk.com/api/v2/issue-tracker-profiles"

payload = json.dumps({
  "issueTrackerType": "jira",
  "name": "Standard-Jira",
  "url": config.jira_url,
  "projectId": args.projectKey,
  #leave the proxy field blank unless needed
  "proxyUrl": "",
  "proxyUsername": "",
  "proxyPassword": "",
  "username": args.jiraUserName,
  "password": args.jiraKey,
  "issueLinkType": "Relates",
  "weaknessPriority": "Highest",
  "userAsReporter": "TRUE",
  #"tags": [
    #"<string>",
    #"<string>"
  #],
  #"severityLevels": [
    #"<string>",
    #"<string>"
  #],
  #"priorityLevels": [
    #"<string>",
    #"<string>"
  #],
  "openIssueStates": [
    "Proposed",
    "To Do"
  ],
  "closedIssueStates": [
    "Done"
  ],
  "rejectedIssueStates": [
    "Won't Do"
  ]
})
headers = {
  'Content-Type': 'application/json',
  'Accept': 'application/hal+json',
  'api-token': args.apiKey
}

create_response = requests.post(url, headers=headers, data=payload)

if create_response.status_code == 200:
    print(create_response.status_code, "- Unpublished ITP Created")

else:
    print("Creation Failed...","\n",create_response.text)

# Parse the JSON response
response_data = json.loads(create_response.text)

# Extract the 'id' value and store it as a variable
id_value = response_data['id']
print(create_response.status_code," ITP ID - ",id_value, " Available for Updating")

# 2nd API call to fetch and additional required information that needs to be mapped for this ITP.

url = f"https://{args.subDomain}.iriusrisk.com/api/v2/issue-tracker-profiles/{id_value}/fetch"

payload = {
}
headers = {
  'Accept': 'application/hal+json',
  'api-token': args.apiKey
}

response = requests.post(url, headers=headers, data=payload)

if response.status_code == 200:
    print(response.status_code," ITP Details Fetched, ready to update")
else:
    print("ITP FETCH FAILED...","\n",response.text)

# 3rd API call to add additional required fields
url = f"https://{args.subDomain}.iriusrisk.com/api/v2/issue-tracker-profiles/{id_value}"

payload = json.dumps({
  "issueTrackerType": "jira",
  "name": "Standard-Jira",
  "url": config.jira_url,
  "projectId": args.projectKey,
  #leave the proxy field blank unless needed
  "proxyUrl": "",
  "proxyUsername": "",
  "proxyPassword": "",
  "username": args.jiraUserName,
  "password": args.jiraKey,
  "openIssueStates": [
      "Proposed",
      "To Do"
    ],
    "closedIssueStates": [
      "Done"
    ],
    "rejectedIssueStates": [
      "Won't Do"
    ],
  "issueLinkType": "Relates",
  "weaknessPriority": "Highest",
  "userAsReporter": "TRUE",
  "issueType": "Task"
})
headers = {
  'Content-Type': 'application/json',
  'Accept': 'application/hal+json',
  'api-token': args.apiKey
}

response = requests.put(url, headers=headers, data=payload)

if response.status_code == 200:
    print(response.status_code, "- Unpublished ITP Updated with Required Information")
else:
    print(response.status_code, " Update ITP Failed", response.text)

#4th API call to publish this ITP

url = f"https://{args.subDomain}.iriusrisk.com/api/v2/issue-tracker-profiles/{id_value}/publish"

payload = {
    "id": id_value,
    "published": {
        "name": "Standard-Jira",
        "issueTrackerType": "jira",
        "url": config.jira_url,
        "projectId": args.projectKey,
        "proxyUrl": "",
        "proxyUsername": "",
        "proxyPassword": "",
        "username": args.jiraUserName,
        "password": args.jiraKey,
        "issueLinkType": "Relates",
        "weaknessPriority": "Highest",
        "userAsReporter": "TRUE",
        "openIssueStates": ["Proposed", "To Do"],
        "closedIssueStates": ["Done"],
        "rejectedIssueStates": ["Won't Do"],
        "issueType": "Task"
    }
}

headers = {
    'Accept': 'application/hal+json',
    'api-token': args.apiKey,
    'Content-Type': 'application/json'
}

response = requests.post(url, headers=headers, json=payload)
if response.status_code == 200:
    print(response.status_code, "- ITP was successfully published")
else:
    print(response.text)



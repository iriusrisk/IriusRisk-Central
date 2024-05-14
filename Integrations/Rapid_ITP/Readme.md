# Purpose
The purpose of this script is to provide assistance in creating an issue tracker profile through the IriusRisk API. 

# Process

Creating an Issue Tracker profile from the API involves four API calls from initial creation to final publication. 

**Call 1 - POST the unpublished ITP**
- This performs the initial creation of the Issue Tracker profile. 

**Call 2 - FETCH the unpublished ITP available options**
- This fetch collects the additional required information about the ITP. For example, the types of issues allowed or any additional fields that are required from Jira. 

**Call 3 - PUT the additional requirements to the ITP**
- This call updates the ITP based on what was available from the previous FETCH call. 
- This would include information like issueType and additional fields. 

**Call 4 - POST to publish the ITP**
- This call transitions the unpublished ITP to published. 

# Requirements

**Setup the virtual environment**
```bash
python3 -m venv IriusRisk-API && cd IriusRisk-API/ && source bin/activate && echo Virtual environment created and active && git clone https://github.com/iriusrisk/IriusRisk-Central.git && echo IriusRisk Github repo cloned
```
**Install the script dependencies**

```bash
pip install requests argparse
```

**Add the url of the Jira instance to the config.py file.** 

```bash
vim config.py
```
```bash
jira_url = "https://<yourJiraUrl>.atlassian.net"
```
# Creating the Issue Tracker Profile

**Call the script and provide the following arguments**

```bash
python3 IriusRisk-Central/Integrations/Rapid_ITP/create_itp_jira.py/ --subDomain r1 --apiKey <apikey> --jiraUserName <jrabe@yourdomain.com> --jiraKey <jira api key> --projectKey <jira project key>
```

Additional descriptions can be found by requesting help from the script. 
```bash
% python3 create_itp_jira.py --help
```

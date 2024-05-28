# IriusRisk GitHub Integration

This project provides an API-driven approach using Python to integrate GitHub as an issue tracker for IriusRisk. There are three main files:

- `config.py`
- `GHSetup.py`
- `GH_POST.py`
- `GH_Sync.py`

## Overview

This project automates the creation and synchronization of GitHub issues with IriusRisk countermeasures, ensuring seamless issue tracking and updates between the two platforms.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Configuration](#configuration)
- [Usage](#usage)
- [Setup in IriusRisk](#setup-in-iriusrisk)
- [Script Details](#script-details)

## Prerequisites

- Enable the API in IriusRisk settings.
- Obtain a valid IriusRisk API token.
- Ensure the API token is associated with an account with the necessary permissions.

## Configuration

Update `config.py` with your configuration details.

### IriusRisk Configuration

```python
#----IriusRisk----
domain = 'https://<insert_IriusRisk_domain>.iriusrisk.com'
sub_url = '/api/v1/products' #initialise
sub_url_api_v2 = '/api/v2/projects'
apitoken = '<insert_IriusRisk_api_token>' #IriusRisk API token
head = {'api-token': apitoken}

#----Github----
owner = "<insert_github_organization>" #GH org
repo = "<insert_github_repo>" #GH project
personal_access_token = "<insert_Github_personal_access_token>" #GH Personal access token
GH_head = {'Authorization': 'Bearer ' + personal_access_token}
```
Note: Replace all placeholder values with your actual configuration details.

## Usage
Run the scripts using Python 3:

```bash
python3 GH_POST.py
python3 GH_Sync.py
```
Note: The actions described below occur only when the respective script is executed. If you wish to automate these actions at regular intervals, consider setting up a scheduled task or cron job.

## Setup in IriusRisk

- Create a project custom field in IriusRisk named `IssueTrackerType` with the options `native` and `GitHub`.
- When `GitHub` is selected and a countermeasure is in the `required` state, a new issue will be created in GitHub. This issue will be linked back to IriusRisk via a countermeasure reference.

## Script Details

### GHSetup.py

- This script defines a class `GithubIssueTracker` to interact with GitHub. It includes methods for creating issues in a specified GitHub repository.
- **Note:** Users do not need to interact with this script directly.

### GH_POST.py

- This script creates an issue in GitHub when the `IssueTrackerType` is set to `GitHub` and a countermeasure is required.
- It links the created GitHub issue back to IriusRisk.

### GH_Sync.py

- This script provides a two-way synchronization between IriusRisk and GitHub.

  **IriusRisk to GitHub:**
  - Monitors comments in IriusRisk and posts new comments to the corresponding GitHub issue.

  **GitHub to IriusRisk:**
  - Monitors comments in GitHub and posts them back to IriusRisk.
  - Monitors issue status in GitHub and updates the countermeasure status in IriusRisk to `implemented` when the GitHub issue is closed.

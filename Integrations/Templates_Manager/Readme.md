# Purpose

The purpose of this script is to collect templates from a GitHub repo, download those locally to a local repo and then post those to the IriusRisk API. 

# Installation

Run the setup.py script to install the script dependencies

```python
python .\setup.py install
```

Update the config.py file with the required variables: 
```python
# API URL and Token
url = "https://insert_your_domain.iriusrisk.com/api/v2/templates/import"
api_token = 'insert_your_api_token'

# GitHub
repo_url = "insert_your_repo_root_url"
repo_sub_folder = "insert_your_sub_folder_if_needed"
```

# Execute the download and import of templates

```python
python .\templates_manager.py 
```
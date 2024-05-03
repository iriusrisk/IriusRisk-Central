# Purpose

The purpose of this script is to collect templates from a GitHub repo, download those locally to a local repo and then post those to the IriusRisk API. 


# Installation

Setup the virtual file and clone the GitHub environment

```bash
python3 -m venv env_name

source env_name/bin/activate

git clone https://github.com/IriusRisk/IriusRisk-Central.git
```

Navigate to the Templates_Manager Folder

```bash
cd Integrations/Templates_Manager
```

Install the dependencies for this script. 

```python
pip install requests==2.31.0 GitPython==3.1.43 tqdm==4.66.2
```

# Execute the script and provide the neccessary arguments to run the script

```python
python3 templates_manager_v2.py --subdomain release --api_token <api_key>
```
This will perform the following actions - 
1. Check if the repo has all of the templates and clone the IriusRisk repo containing the Templates if it does not
2. If that repo already exists, it will attempt to update the local repo with any new templates
3. It will post any template found to the templates endpoint through the API
4. It will post any libraries found to the libraries endpoint through the API
5. Status of the overall migration will be displayed
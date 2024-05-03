import os
import shutil
import requests
import xml.etree.ElementTree as ET
from git import Repo
from tqdm import tqdm
import argparse

# Set up command line arguments
parser = argparse.ArgumentParser(description="Upload XML files to IriusRisk as templates or libraries.")
parser.add_argument("--subdomain", type=str, required=True, help="The subdomain for the IriusRisk API.")
parser.add_argument("--api_token", type=str, required=True, help="API token for authentication with the IriusRisk API.")
args = parser.parse_args()

# API and GitHub Configuration
base_url = f"https://{args.subdomain}.iriusrisk.com/api/v2"
api_url_templates = f"{base_url}/templates/import"
api_url_libraries = f"{base_url}/libraries/import"

repo_url = "https://github.com/iriusrisk/IriusRisk-Central.git"
repo_sub_folder = "Templates/IR_Published_Templates"
repo_path = os.path.join(os.getcwd(), "cloned_repo")

try:
    # Clone or update repository
    if not os.path.exists(repo_path):
        print("Cloning repository...")
        Repo.clone_from(repo_url, repo_path)
        print("Repository cloned successfully.")
    else:
        print("Repository already exists. Updating...")
        repo = Repo(repo_path)
        origin = repo.remote(name='origin')
        origin.pull()
        print("Repository updated.")

    templates_dir = os.path.join(repo_path, repo_sub_folder)
    if not os.path.exists(templates_dir):
        print("IR_Published_Templates directory not found.")
        exit()
    print("IR_Published_Templates directory found.")

    templates_contents = os.listdir(templates_dir)
    if not templates_contents:
        print("No files found in the IR_Published_Templates directory.")
        exit()

    files_to_process = [file for file in templates_contents if file.endswith(".xml")]
    if not files_to_process:
        print("No XML files found to process.")
        exit()

    results = []
    with tqdm(total=len(files_to_process), desc="Processing files", leave=False) as pbar:
        for file_name in files_to_process:
            file_path = os.path.join(templates_dir, file_name)
            tree = ET.parse(file_path)
            root = tree.getroot()

            is_template = root.tag.lower() == 'template'  # Adjust this condition based on your XML schema

            if not is_template:
                # Process as library
                with open(file_path, 'rb') as f:
                    files = {
                        'file': (file_name, f, 'application/xml'),
                        'name': (None, os.path.splitext(file_name)[0]),
                        'referenceId': (None, os.path.splitext(file_name)[0])
                    }
                    headers = {
                        'Accept': 'application/hal+json',
                        'api-token': args.api_token
                    }
                    response = requests.post(api_url_libraries, headers=headers, files=files)
                    result_message = f"{file_name} imported as a library into {args.subdomain}. Status: {response.status_code}"
                    if response.status_code != 200:
                        result_message += f", Error: {response.text}"
                    results.append(result_message)
            else:
                # Process as template
                with open(file_path, 'rb') as f:
                    files = {
                        'file': (file_name, f, 'application/xml'),
                        'name': (None, os.path.splitext(file_name)[0].replace("-", " ").capitalize()),
                        'referenceId': (None, os.path.splitext(file_name)[0].lower())
                    }
                    headers = {
                        'Accept': 'application/hal+json',
                        'api-token': args.api_token
                    }
                    response = requests.post(api_url_templates, headers=headers, files=files)
                    result_message = f"{file_name} imported as a template into {args.subdomain}. Status: {response.status_code}"
                    if response.status_code != 200:
                        result_message += f", Error: {response.text}"
                    results.append(result_message)
            pbar.update(1)

    # Print all results clearly after processing
    print("Processing complete. Results:")
    for result in results:
        print(result)

except Exception as e:
    print("An error occurred:", e)

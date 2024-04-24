from git import Repo
import requests
import os
import config

# Set up the path for cloning
repo_path = os.path.join(os.getcwd(), "cloned_repo")
repo_url = config.repo_url

# Clone the repository if the directory doesn't exist
if not os.path.exists(repo_path):
    os.makedirs(repo_path)
    Repo.clone_from(repo_url, repo_path)
    print("Repository cloned successfully.")
    print("Working on importing templates now...")
else:
    print("Directory already exists and is assumed to contain the necessary files.")
    print("Working on importing templates now...")

def get_files(directory, extension):
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(extension):
                yield os.path.join(root, file)

# Define the directory where the Templates folder is located
templates_dir = os.path.join(repo_path, config.repo_sub_folder)

# Example usage: finding all XML files in the Templates directory
files_to_process = list(get_files(templates_dir, ".xml"))

# API URL and Token
url = config.url
api_token = config.api_token

# Iterate over each XML file and send it
for file_path in files_to_process:
    with open(file_path, 'rb') as f:
        # Use the filename (without extension) as the name
        file_name = os.path.basename(file_path)
        file_base_name = os.path.splitext(file_name)[0]

        # Define the payload
        files = {
            'file': (file_name, f, 'application/xml'),
            'name': (None, file_base_name.replace("-"," ").capitalize()),  # Using the filename without extension as the name
            'referenceId': (None, file_base_name.lower())  # You may modify 'referenceId' as needed
        }

        headers = {
            'Accept': 'application/hal+json',
            'api-token': api_token
        }

        # Send the request
        response = requests.post(url, headers=headers, files=files)

        if response.status_code == 200:
            print(file_base_name, "Successfully Imported!!!")
        else:
            print(f"File: {file_name}, Status Code: {response.status_code}, Response: {response.text}")

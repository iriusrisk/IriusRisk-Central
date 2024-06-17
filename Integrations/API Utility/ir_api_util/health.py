import os
import requests

class Health:
    def __init__(self, instance_domain_path):
        self.instance_domain_path = instance_domain_path

    def test_api_health(self):
        instance_domain = self.read_instance_domain()
        if instance_domain is None:
            print("Instance domain is None. Exiting health check.")
            return False
        endpoint_url = f'https://{instance_domain}.iriusrisk.com/health'
        print(f"Checking health at URL: {endpoint_url}")
        try:
            # Set a timeout for the request
            response = requests.get(endpoint_url, timeout=10)
            print(f"Received response: {response.status_code}")
            response.raise_for_status()
            return response.status_code == 200
        except requests.exceptions.Timeout:
            print("Request timed out.")
            return False
        except requests.RequestException as e:
            print(f"API health check failed: {e}")
            return False

    def read_instance_domain(self):
        try:
            with open(self.instance_domain_path, 'r') as file:
                return file.read().strip()
        except FileNotFoundError:
            print(f"File not found: {self.instance_domain_path}")
            return None

if __name__ == "__main__":
    print("Starting script execution.")
    instance_file_path = os.path.expanduser("~/ir/ir_instance_domain")
    print(f"Instance file path: {instance_file_path}")
    token_file_path = os.path.expanduser("~/ir/.ir_user_token")
    print(f"Token file path: {token_file_path}")

    print("Initializing Auth class.")
    auth = Auth()
    print("Checking user instance file.")
    auth.check_user_instance_file(instance_file_path)
    print("Checking user token file.")
    auth.check_user_token_file(token_file_path)

    print("Initializing Health class.")
    health = Health(instance_file_path)
    print("Testing API health.")
    if health.test_api_health():
        print("API health check passed.")
        print("Initializing Reception class.")
        reception = Reception()
        print("Executing Reception main method.")
        print("")
        reception.main()
    else:
        print("Exiting due to failed API health check.")

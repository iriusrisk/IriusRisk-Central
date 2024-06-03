import os
import requests

class Health:
    def __init__(self, instance_domain_path):
        self.instance_domain_path = instance_domain_path

    def test_api_health(self):
        instance_domain = self.read_instance_domain()
        endpoint_url = f'https://{instance_domain}.iriusrisk.com/health'
        try:
            response = requests.get(endpoint_url, headers={'Accept': 'application/json'})
            response.raise_for_status()
            return response.status_code == 200
        except requests.RequestException as e:
            print(f"API health check failed: {e}")
            return False

    def read_instance_domain(self):
        try:
            with open(self.instance_domain_path, 'r') as file:
                return file.read().strip()
        except FileNotFoundError:
            print("Instance domain file not found.")
            return None

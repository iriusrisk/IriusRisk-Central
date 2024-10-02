import sys
import requests
import os
import json
from deepdiff import DeepDiff
from auth import Auth

# Function to load queries from the JSON file
def load_queries(filename):
    try:
        with open(filename, 'r') as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error reading {filename}: {e}")
        sys.exit(1)

# Read config file for output path and page size
def read_config(config_path):
    try:
        with open(config_path, 'r') as config_file:
            config = json.load(config_file)
            output_path = os.path.expanduser(config.get('output_path', '~/'))
            os.makedirs(output_path, exist_ok=True)
            page_size = config.get('page_size', 2000)
            return output_path, page_size
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error reading config file: {e}. Defaulting to home directory.")
        output_path = os.path.expanduser('~/')
        os.makedirs(output_path, exist_ok=True)
        return output_path, 2000

# Function to compare types
def compare_types(expected, actual):
    # If the expected value is None, allow any actual value
    if expected is None:
        return True, None  # Null means any value is valid

    # If the actual value is None, allow it for any expected type
    if actual is None:
        return True, None  # Null is acceptable for any expected type

    if isinstance(expected, dict) and isinstance(actual, dict):
        for key in expected:
            if key not in actual:
                return False, f"Missing key: {key}"
            match, error = compare_types(expected[key], actual[key])
            if not match:
                return False, error
    elif isinstance(expected, list) and isinstance(actual, list):
        if len(expected) == 0 or len(actual) == 0:
            return True, None  # Allow empty lists
        return compare_types(expected[0], actual[0])
    else:
        # For string types
        if expected == "string" and isinstance(actual, str):
            return True, None
        # For int types (ensuring bools are not mistaken for ints)
        elif expected == "int" and isinstance(actual, int) and not isinstance(actual, bool):
            return True, None
        # For bool types
        elif expected == "bool" and isinstance(actual, bool):
            return True, None
        # For float types
        elif expected == "float" and isinstance(actual, float):
            return True, None
        # For list types
        elif expected == "list" and isinstance(actual, list):
            return True, None
        # For dict types
        elif expected == "dict" and isinstance(actual, dict):
            return True, None
        else:
            return False, f"Type mismatch: expected {expected}, got {type(actual).__name__}"
    
    return True, None


# Class to handle API checking
class APIChecker:
    def __init__(self, api_token_path='~/ir/.ir_user_token', instance_domain_path='~/ir/ir_instance_domain'):
        self.auth = Auth()
        self.api_token_path = os.path.expanduser(api_token_path)
        self.instance_domain_path = os.path.expanduser(instance_domain_path)
        self.auth.check_user_instance_file(self.instance_domain_path)
        self.auth.check_user_token_file(self.api_token_path)
        self.api_token, self.instance_domain = self.read_credentials()
        script_dir = os.path.dirname(os.path.realpath(__file__))
        self.output_path, self.page_size = read_config(os.path.join(script_dir, 'config.json'))

    def read_credentials(self):
        try:
            with open(self.api_token_path, 'r') as token_file:
                api_token = token_file.read().strip()
            with open(self.instance_domain_path, 'r') as domain_file:
                instance_domain = domain_file.read().strip()
            return api_token, instance_domain
        except FileNotFoundError as e:
            print(f"Error: {e}. Make sure the paths are correct.")
            sys.exit(1)  # Exit if credentials cannot be read

    def test_endpoint(self, endpoint):
        method = endpoint.get("method", "GET").upper()
        relative_url = endpoint["url"]

        # Ensure the URL is properly formatted
        if not relative_url.startswith("http"):
            url = f"https://{self.instance_domain}.iriusrisk.com{relative_url}"
        else:
            url = relative_url

        headers = endpoint.get("headers", {})
        headers['api-token'] = self.api_token  # Use the stored API token
        expected_status = endpoint["expected_status"]
        expected_response = endpoint["expected_response"]

        try:
            response = requests.request(method, url, headers=headers)
        except requests.exceptions.RequestException as e:
            print(f"Error fetching {url}: {e}")
            return False

        status_code = response.status_code
        try:
            response_json = response.json()
        except json.JSONDecodeError:
            print(f"Invalid JSON response from {url}")
            return False

        print(f"Testing {endpoint['name']} - {method} {url}")
        print(f"Expected Status: {expected_status}, Actual Status: {status_code}")

        if status_code != expected_status:
            print(f"Status Code Mismatch! Expected {expected_status}, got {status_code}")
            return False

        # Compare response JSON structure with expected structure
        if isinstance(response_json, list) and isinstance(expected_response, list):
            for i, item in enumerate(response_json):
                match, error = compare_types(expected_response[0], item)
                if not match:
                    print(f"Response Mismatch at item {i}! {error}")
                    print(f"Expected: {expected_response[0]}\nGot: {item}")
                    return False
        else:
            match, error = compare_types(expected_response, response_json)
            if not match:
                print(f"Response Mismatch Found! {error}")
                print(f"Expected: {expected_response}\nGot: {response_json}")
                return False

        print("Test Passed!")
        return True

    def run_tests(self, queries):
        print(f"Found {len(queries['endpoints'])} endpoints to test.")
        for i, endpoint in enumerate(queries['endpoints']):
            print(f"Running test {i + 1} of {len(queries['endpoints'])}...")
            success = self.test_endpoint(endpoint)
            if not success:
                print(f"Test Failed for {endpoint['name']}!\n")
            else:
                print(f"Test Succeeded for {endpoint['name']}!\n")

def main():
    script_dir = os.path.dirname(os.path.realpath(__file__))
    api_checker = APIChecker()
    queries = load_queries(os.path.join(script_dir, 'apiChecker.json'))
    api_checker.run_tests(queries)

# Proper entry point check
if __name__ == "__main__":
    main()

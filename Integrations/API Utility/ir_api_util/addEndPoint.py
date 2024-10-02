import sys
import json
import os



def parse_sample_response(sample):
    if isinstance(sample, dict):
        parsed = {}
        for key, value in sample.items():
            if value is None:
                parsed[key] = None  # Allow None values
            elif isinstance(value, bool):
                parsed[key] = "bool"
            elif isinstance(value, str):
                parsed[key] = "string"
            elif isinstance(value, int):
                parsed[key] = "int"
            elif isinstance(value, float):
                parsed[key] = "float"
            elif isinstance(value, list):
                if not value:
                    parsed[key] = []  # Empty list
                else:
                    if isinstance(value[0], dict):
                        parsed[key] = [parse_sample_response(value[0])]
                    elif isinstance(value[0], str):
                        parsed[key] = ["string"]  # Handle lists of strings
                    else:
                        parsed[key] = ["unknown"]
            elif isinstance(value, dict):
                parsed[key] = parse_sample_response(value)
            else:
                parsed[key] = "unknown"
        return parsed
    elif isinstance(sample, list):
        if not sample:
            return []
        elif isinstance(sample[0], dict):
            return [parse_sample_response(sample[0])]
        else:
            return ["string"] if isinstance(sample[0], str) else ["unknown"]
    else:
        return "unknown"



def read_credentials(api_token_path='~/ir/.ir_user_token', instance_domain_path='~/ir/ir_instance_domain'):
    try:
        with open(os.path.expanduser(instance_domain_path), 'r') as domain_file:
            instance_domain = domain_file.read().strip()
        return instance_domain
    except FileNotFoundError as e:
        print(f"Error: {e}. Make sure the paths are correct.")
        sys.exit(1)  # Exit if credentials cannot be read



def add_endpoint_to_queries(name, method, url, sample_structure, instance_domain, filename='apiChecker.json'):
    parsed_structure = parse_sample_response(sample_structure)

    if not url.startswith("https://") and not url.startswith("http://"):
        url = f"https://{instance_domain}.iriusrisk.com{url}"

    # Detect if it's v1 or v2 based on the URL pattern
    if "/v2/" in url:
        accept_header = "application/hal+json"
    else:
        accept_header = "application/json"

    new_endpoint = {
        "name": name,  # Use the provided name
        "method": method.upper(),
        "url": url,
        "headers": {
            "Accept": accept_header  # Use the correct Accept header based on v1 or v2
        },
        "expected_status": 200,
        "expected_response": parsed_structure
    }

    try:
        if not os.path.exists(filename):
            print(f"{filename} not found, creating a new one.")
            data = {"endpoints": [new_endpoint]}
            with open(filename, 'w') as file:
                json.dump(data, file, indent=4)
        else:
            with open(filename, 'r+') as file:
                try:
                    data = json.load(file)
                    data['endpoints'].append(new_endpoint)
                except json.JSONDecodeError:
                    data = {"endpoints": [new_endpoint]}
                file.seek(0)
                json.dump(data, file, indent=4)
        print(f"Successfully added the endpoint {name} to {filename}.")
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error handling {filename}: {e}")




def main():
    if len(sys.argv) != 5:
        print("Usage: python3 addEndPoint.py <Name> <HTTP Method> <URL> <sample_output_file>")
        sys.exit(1)

    name = sys.argv[1]  # Take the name as an argument
    method = sys.argv[2].upper()
    url = sys.argv[3]
    sample_output_file = sys.argv[4]

    valid_methods = ["GET", "POST", "PUT", "DELETE"]
    if method not in valid_methods:
        print(f"Error: Unsupported HTTP method '{method}'. Supported methods are {', '.join(valid_methods)}.")
        sys.exit(1)

    try:
        with open(sample_output_file, 'r') as f:
            sample_structure = json.load(f)
    except json.JSONDecodeError as e:
        print(f"Error parsing sample output: {e}")
        sys.exit(1)

    instance_domain = read_credentials()

    add_endpoint_to_queries(name, method, url, sample_structure, instance_domain)

if __name__ == "__main__":
    main()

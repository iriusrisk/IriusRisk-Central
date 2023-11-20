import requests
import json
import config

url_get = config.url_get
headers_get = {
    'Accept': 'application/json',
    'api-token': config.url_get_api_key
}

# Make the GET request to fetch existing business units
response_get = requests.get(url_get, headers=headers_get)
business_units_existing = json.loads(response_get.text)

# Check if business_units_existing is a list before proceeding
if isinstance(business_units_existing, list):
    url_post = config.url_post

    # Iterate through each business unit in the list
    for unit_index, business_unit in enumerate(business_units_existing, start=1):
        payload = json.dumps(business_unit)
        headers_post = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "API-token": config.url_post_api_key,
        }

        # Make the POST request
        response_post = requests.post(url_post, headers=headers_post, data=payload)

        # Check the response status code and print the result
        if response_post.status_code == 201:  # Assuming 201 is a successful response code
            print(f"API call {unit_index} was successful. Response: {response_post.text}")
        else:
            print(f"API call {unit_index} failed. Status Code: {response_post.status_code}, Response: {response_post.text}")
else:
    print("Invalid format for existing business units.")

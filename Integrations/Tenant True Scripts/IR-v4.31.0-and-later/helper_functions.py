import pip._vendor.requests as requests
import sys
import logging

# Setting up logging
logger = logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


# Handles whatever response we get from requests
def handle_response(response, url):
    if response.status_code == 200:
        logging.info(
            f"Request {response.request.method} {url} successful with status code {response.status_code}"
        )
        return response.json()
    elif response.status_code == 401:
        logging.error(
            "User is unauthorized. Please check if your API token is valid, API is enabled in settings, and you have appropriate permissions."
        )
        sys.exit()
    else:
        logging.error(
            f"Request {response.request.method} {url} failed with status code {response.status_code}"
        )


# GET request
def get_request(base_url, endpoint, headers):
    url = base_url + endpoint
    response = requests.get(url, headers=headers)
    return handle_response(response, url)


# PUT request
def put_request(uuid, json_object, url, headers):
    response = requests.put(url + "/" + uuid, headers=headers, json=json_object)
    return handle_response(response, url)


# POST request
def post_request(json_object, url, headers):
    response = requests.post(url, headers=headers, json=json_object)
    return handle_response(response, url)


# Finds the matches between 2 fields in 2 lists
def find_matches(list_1, list_2, field):
    combined = list_1 + list_2

    variable_to_match = []
    for i in range(0, len(combined)):
        variable_to_match.append(combined[i][field])

    matches = {x for x in variable_to_match if variable_to_match.count(x) > 1}

    matches_dict = {}

    for role in list_2:
        if role[field] in matches:
            matches_dict[role[field]] = role["id"]

    return matches_dict

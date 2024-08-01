import pip._vendor.requests as requests
import sys
import json
import config

def get_api_data(url, headers):
    """Function to perform a GET request."""
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        print("GET request successful")
        return response.json()
    elif response.status_code == 401:
        print("User is unauthorized. Please check your API token and permissions.")
        sys.exit()
    else:
        print(f"GET request failed for {url}: {response.status_code} {response.text}")
        return None

def post_api_data(url, headers, data):
    """Function to perform a POST request."""
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200:
        print("POST successful")
        return response.json()
    elif response.status_code == 401:
        print("User is unauthorized. Please check your API token and permissions.")
        sys.exit()
    else:
        print(f"POST request failed for {url}: {response.status_code} {response.text}")
        return None

def get_or_create_type(item, post_url, post_headers):
    """Ensure type exists and return its ID; create new if not found."""
    response = get_api_data(post_url, post_headers)
    if response:
        for type_item in response['_embedded']['items']:
            if type_item['name'] == item['name']:
                return item['id'], type_item['id']

    # Create new type if not found
    type_data = {"name": item['name'], "description": item['description'], "multiSelectable": item['multiSelectable']}
    new_type_response = post_api_data(post_url, post_headers, type_data)
    if new_type_response:
        return item['id'], new_type_response['id']
    return None, None

def get_or_create_group(item, post_url, post_headers):
    """Ensure group exists and return its ID; create new if not found."""
    response = get_api_data(post_url, post_headers)
    if response:
        for group_item in response['_embedded']['items']:
            if group_item['name'] == item['name']:
                return group_item['id']

    # Create new group if not found
    group_data = {"name": item['name'], "entity": item['entity']}
    new_group_response = post_api_data(post_url, post_headers, group_data)
    return new_group_response['id']

def get_type_values(type_id, url, headers):
    """Fetch values for a specific custom field type."""
    response = requests.get(f"{url}/{type_id}/values", headers=headers)
    if response.status_code == 200:
        print("Successfully retrieved type values")
        return response.json()['_embedded']['items']
    else:
        print(f"Failed to retrieve values for type ID {type_id}: {response.status_code} {response.text}")
        return []

def post_type_values(type_id, values, url, headers):
    """Post values to a specific custom field type in the POST domain."""
    for value in values:
        data = {'value': value['value']}
        response = requests.post(f"{url}/{type_id}/values", headers=headers, json=data)
        if response.status_code == 200:
            print(f"Successfully posted value {data['value']} to type ID {type_id}")
        else:
            print(f"Failed to post value {data['value']} to type ID {type_id}: {response.status_code} {response.text}")

def main():
    start_headers = {'api-token': config.start_apitoken}
    post_headers = {'api-token': config.post_apitoken}
    type_ids_mapping = {}

    # Handle types
    start_url_type = config.start_domain + '/api/v2/custom-fields/types'
    post_url_type = config.post_domain + '/api/v2/custom-fields/types'
    types_data = get_api_data(start_url_type, start_headers)
    if types_data:
        for item in types_data['_embedded']['items']:
            start_type_id, post_type_id = get_or_create_type(item, post_url_type, post_headers)
            if start_type_id and post_type_id:
                type_ids_mapping[start_type_id] = post_type_id
                print(f"Handled type {item['name']} with GET ID {start_type_id} and POST ID {post_type_id}")

    # Get and post values for types
    for start_type_id, post_type_id in type_ids_mapping.items():
        values = get_type_values(start_type_id, config.start_domain + '/api/v2/custom-fields/types', start_headers)
        post_type_values(post_type_id, values, config.post_domain + '/api/v2/custom-fields/types', post_headers)

    # Handle groups
    start_url_group = config.start_domain + '/api/v2/custom-fields/groups'
    post_url_group = config.post_domain + '/api/v2/custom-fields/groups'
    groups_data = get_api_data(start_url_group, start_headers)
    if groups_data:
        for item in groups_data['_embedded']['items']:
            group_id = get_or_create_group(item, post_url_group, post_headers)
            print(f"Handled group {item['name']} with ID {group_id}")

    # Handle custom fields
    start_url_cf = config.start_domain + '/api/v2/custom-fields'
    post_url_cf = config.post_domain + '/api/v2/custom-fields'
    cfs_data = get_api_data(start_url_cf, start_headers)
    if cfs_data:
        for item in cfs_data['_embedded']['items']:
            cf_data = {
                "name": item['name'],
                "description": item['description'],
                "referenceId": item['referenceId'],
                "entity": item['entity'],
                "required": item['required'],
                "visible": item['visible'],
                "editable": item['editable'],
                "exportable": item['exportable'],
                "defaultValue": item['defaultValue'],
                "maxSize": item['maxSize'],
                "regexValidator": item['regexValidator'],
                "typeId": type_ids_mapping[item['type']['id']]
            }

            # Only add groupId if 'group' key exists and is not None
            if 'group' in item and item['group'] is not None:
                group_id = get_or_create_group(item['group'], post_url_group, post_headers)
                if group_id:
                    cf_data['groupId'] = group_id

            print("Posting custom field with data:", cf_data)
            post_response = post_api_data(post_url_cf, post_headers, cf_data)
            if post_response:
                print(f"Custom field {item['name']} posted successfully.")
            else:
                print(f"Failed to post custom field {item['name']}. Data used: {cf_data}")

if __name__ == "__main__":
    main()

import pip._vendor.requests as requests
import config
import constants
import helper_functions
import logging
import mappers

# TODO needs finished
# TODO what is a group id ?????
# TODO ask questions about the group id

def get_or_create_type(item, post_url, post_headers):
    """Ensure type exists and return its ID; create new if not found."""
    response = helper_functions.get_request(post_url, endpoint='', headers=post_headers)
    if response:
        for type_item in response['_embedded']['items']:
            if type_item['name'] == item['name']:
                return item['id'], type_item['id']

    # Create new type if not found
    type_data = {"name": item['name'], "description": item['description'], "multiSelectable": item['multiSelectable']}
    new_type_response = helper_functions.post_request(type_data, post_url, post_headers)
    if new_type_response:
        return item['id'], new_type_response['id']
    return None, None

def get_or_create_group(item, post_url, post_headers):
    """Ensure group exists and return its ID; create new if not found."""
    response = helper_functions.get_request(post_url, endpoint=None, headers=post_headers)
    if response:
        for group_item in response['_embedded']['items']:
            if group_item['name'] == item['name']:
                return group_item['id']

    # Create new group if not found
    group_data = {"name": item['name'], "entity": item['entity']}
    new_group_response = helper_functions.post_request(group_data, post_url, post_headers)
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
        data = {'value': value['value'],
                'after': ''}
        print(data)
        response = requests.post(f"{url}/{type_id}/values", headers=headers, json=data)
        if response.status_code == 200:
            logging.info(f"Successfully posted value {data['value']} to type ID {type_id}")
        else:
            # TODO Figure out why this is failing
            logging.error(f"Failed to post value {data['value']} to type ID {type_id}: {response.status_code} {response.text}")

def main():
    type_ids_mapping = {}

    # Handle types
    types_data = helper_functions.get_request(config.start_domain, constants.ENDPOINT_CUSTOM_FIELDS_TYPES, config.start_head)
    if types_data:
        for item in types_data['_embedded']['items']:
            start_type_id, post_type_id = get_or_create_type(item, config.post_domain + constants.ENDPOINT_CUSTOM_FIELDS_TYPES, config.post_head)
            if start_type_id and post_type_id:
                type_ids_mapping[start_type_id] = post_type_id
                logging.info(f"Handled type {item['name']} with GET ID {start_type_id} and POST ID {post_type_id}")

    # Get and post values for types
    for start_type_id, post_type_id in type_ids_mapping.items():
        values = get_type_values(start_type_id, config.start_domain + constants.ENDPOINT_CUSTOM_FIELDS_TYPES, config.start_head)
        post_type_values(post_type_id, values, config.post_domain + constants.ENDPOINT_CUSTOM_FIELDS_TYPES, config.post_head)

    # Handle groups
    post_url_group = config.post_domain + constants.ENDPOINT_CUSTOM_FIELDS_GROUPS
    groups_data = helper_functions.get_request(config.start_domain, constants.ENDPOINT_CUSTOM_FIELDS_GROUPS, config.start_head)
    if groups_data:
        for item in groups_data['_embedded']['items']:
            group_id = get_or_create_group(item, post_url_group, config.post_head)
            logging.info(f"Handled group {item['name']} with ID {group_id}")

    # Handle custom fields
    source_cfs_data = helper_functions.get_request(config.start_domain, constants.ENDPOINT_CUSTOM_FIELDS, config.start_head)
    dest_cfs_data = helper_functions.get_request(config.post_domain, constants.ENDPOINT_CUSTOM_FIELDS, config.post_head)

    mapped_source_cfs_data = mappers.map_custom_fields(source_cfs_data, type_ids_mapping)
    mapped_dest_cfs_data = mappers.map_custom_fields(dest_cfs_data, type_ids_mapping)

    matches = helper_functions.find_matches(mapped_source_cfs_data, mapped_dest_cfs_data, 'referenceId')


    if source_cfs_data:
        for item in source_cfs_data['_embedded']['items']:

            cf_data = mappers.map_single_custom_field(item, type_ids_mapping)
            print("cf_data")
            print(cf_data)

            # Default groupId to None
            cf_data['groupId'] = None
            cf_data['after'] = ''

            # Only add groupId if 'group' key exists and is not None
            if 'group' in item and item['group'] is not None:
                group_id = get_or_create_group(item['group'], post_url_group, config.post_head)
                if group_id:
                    cf_data['groupId'] = group_id
            

            if cf_data['referenceId'] in matches:
                if helper_functions.is_ir_object_same(mappers.map_single_custom_field(item, type_ids_mapping), mapped_dest_cfs_data) is False:
                    uuid = matches[cf_data['referenceId']]
                    del cf_data['id']
                    del cf_data['referenceId']
                    print(cf_data)
                    helper_functions.put_request(uuid, cf_data, config.post_domain + constants.ENDPOINT_CUSTOM_FIELDS, config.post_head)
            else :
                print("cf_data")
                print(cf_data)
                logging.info("Posting custom field with data:", cf_data)
                helper_functions.post_request(cf_data, config.post_domain, config.post_head)

if __name__ == "__main__":
    main()

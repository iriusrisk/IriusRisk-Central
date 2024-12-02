import pip._vendor.requests as requests
import config
import constants
import helper_functions
import logging
import mappers

# TODO ask questions about the group id


def get_or_create_type(item, dest_url, dest_headers):
    """Ensure type exists and return its ID; create new if not found."""
    response = helper_functions.get_request(dest_url, endpoint="", headers=dest_headers)
    if response:
        for type_item in response["_embedded"]["items"]:
            if type_item["name"] == item["name"]:
                return item["id"], type_item["id"]

    # Create new type if not found
    type_data = {
        "name": item["name"],
        "description": item["description"],
        "multiSelectable": item["multiSelectable"],
    }
    new_type_response = helper_functions.dest_request(type_data, dest_url, dest_headers)
    if new_type_response:
        return item["id"], new_type_response["id"]
    return None, None


def get_or_create_group(item, dest_url, dest_headers):
    """Ensure group exists and return its ID; create new if not found."""
    response = helper_functions.get_request(
        dest_url, endpoint=None, headers=dest_headers
    )
    if response:
        for group_item in response["_embedded"]["items"]:
            if group_item["name"] == item["name"]:
                return group_item["id"]

    # Create new group if not found
    group_data = {"name": item["name"], "entity": item["entity"]}
    new_group_response = helper_functions.dest_request(
        group_data, dest_url, dest_headers
    )
    return new_group_response["id"]


def get_type_values(type_id, url, headers):
    """Fetch values for a specific custom field type."""
    response = requests.get(f"{url}/{type_id}/values", headers=headers)
    if response.status_code == 200:
        logging.info("Successfully retrieved type values")
        return response.json()["_embedded"]["items"]
    else:
        logging.error(
            f"Failed to retrieve values for type ID {type_id}: {response.status_code} {response.text}"
        )
        return []


def dest_type_values(type_id, values, url, headers):
    """Post values to a specific custom field type in the POST domain."""
    for value in values:
        data = {"value": value["value"], "after": ""}

        response = requests.post(f"{url}/{type_id}/values", headers=headers, json=data)
        if response.status_code == 200:
            logging.info(
                f"Successfully posted value {data['value']} to type ID {type_id}"
            )
        else:
            # TODO Figure out why this is failing
            logging.error(
                f"Failed to post value {data['value']} to type ID {type_id}: {response.status_code} {response.text}"
            )


def main(source_domain, dest_domain, source_head, dest_head):
    type_ids_mapping = {}

    # Handle types
    types_data = helper_functions.get_request(
        source_domain, constants.ENDPOINT_CUSTOM_FIELDS_TYPES, source_head
    )
    if types_data:
        for item in types_data["_embedded"]["items"]:
            source_type_id, dest_type_id = get_or_create_type(
                item,
                dest_domain + constants.ENDPOINT_CUSTOM_FIELDS_TYPES,
                dest_head,
            )
            if source_type_id and dest_type_id:
                type_ids_mapping[source_type_id] = dest_type_id
                logging.info(
                    f"Handled type {item['name']} with GET ID {source_type_id} and POST ID {dest_type_id}"
                )

    # Get and post values for types
    for source_type_id, dest_type_id in type_ids_mapping.items():
        values = get_type_values(
            source_type_id,
            source_domain + constants.ENDPOINT_CUSTOM_FIELDS_TYPES,
            source_head,
        )
        dest_type_values(
            dest_type_id,
            values,
            dest_domain + constants.ENDPOINT_CUSTOM_FIELDS_TYPES,
            dest_head,
        )

    # Handle groups
    dest_url_group = dest_domain + constants.ENDPOINT_CUSTOM_FIELDS_GROUPS
    groups_data = helper_functions.get_request(
        source_domain, constants.ENDPOINT_CUSTOM_FIELDS_GROUPS, source_head
    )
    if groups_data:
        for item in groups_data["_embedded"]["items"]:
            group_id = get_or_create_group(item, dest_url_group, dest_head)
            logging.info(f"Handled group {item['name']} with ID {group_id}")

    # Handle custom fields
    source_cfs_data = helper_functions.get_request(
        source_domain, constants.ENDPOINT_CUSTOM_FIELDS, source_head
    )
    dest_cfs_data = helper_functions.get_request(
        dest_domain, constants.ENDPOINT_CUSTOM_FIELDS, dest_head
    )

    mapped_source_cfs_data = mappers.map_custom_fields(
        source_cfs_data, type_ids_mapping
    )
    mapped_dest_cfs_data = mappers.map_custom_fields(dest_cfs_data, type_ids_mapping)

    matches = helper_functions.find_matches(
        mapped_source_cfs_data, mapped_dest_cfs_data, "referenceId"
    )

    if source_cfs_data:
        for item in source_cfs_data["_embedded"]["items"]:
            cf_data = mappers.map_single_custom_field(item, type_ids_mapping)

            # Default groupId to None
            cf_data["groupId"] = None
            cf_data["after"] = ""

            # Only add groupId if 'group' key exists and is not None
            if "group" in item and item["group"] is not None:
                group_id = get_or_create_group(item["group"], dest_url_group, dest_head)
                if group_id:
                    cf_data["groupId"] = group_id

            if cf_data["referenceId"] in matches and cf_data["editable"] is True:
                if (
                    helper_functions.is_ir_object_same(
                        mappers.map_single_custom_field(item, type_ids_mapping),
                        mapped_dest_cfs_data,
                    )
                    is False
                ):
                    uuid = matches[cf_data["referenceId"]]
                    del cf_data["id"]
                    del cf_data["referenceId"]
                    helper_functions.put_request(
                        uuid,
                        cf_data,
                        dest_domain + constants.ENDPOINT_CUSTOM_FIELDS,
                        dest_head,
                    )
            else:
                logging.info("Posting custom field with data:", cf_data)
                print(cf_data)
                del cf_data["id"]
                helper_functions.dest_request(
                    cf_data, dest_domain + constants.ENDPOINT_CUSTOM_FIELDS, dest_head
                )


if __name__ == "__main__":
    logging.info("tenant_config_migration_CustomFields | START")
    main(config.source_domain, config.dest_domain, config.source_head, config.dest_head)
    logging.info("tenant_config_migration_CustomFields | END")

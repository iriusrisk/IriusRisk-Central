import config
import constants
import logging
import helper_functions

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def get_component_categories(domain, headers):
    logging.info(f"Fetching component categories from {domain}")
    response = helper_functions.get_request(
        f"{domain}{constants.ENDPOINT_COMPONENTS_CATEGORIES_SUMMARY}",
        "",
        headers=headers,
    )
    return response["_embedded"]["items"]


def get_component_category(domain, category_id, headers):
    logging.info(f"Fetching component category {category_id} from {domain}")
    response = helper_functions.get_request(
        f"{domain}{constants.ENDPOINT_COMPONENTS_CATEGORIES}/{category_id}",
        "",
        headers=headers,
    )
    return response


def update_component_category(domain, category_id, data, headers):
    logging.info(f"Updating component category {category_id} at {domain}")
    response = helper_functions.put_request(
        category_id,
        data,
        f"{domain}{constants.ENDPOINT_COMPONENTS_CATEGORIES}",
        headers=headers,
    )
    return response


def create_component_category(domain, data, headers):
    logging.info(f"Creating new component category at {domain}")
    response = helper_functions.post_request(
        data,
        f"{domain}{constants.ENDPOINT_COMPONENTS_CATEGORIES}",
        headers=headers,
    )
    return response


def main(source_domain, destination_domain, source_headers, dest_headers):
    logging.info("tenant_config_migration_component_categories | START")
    source_categories = get_component_categories(source_domain, source_headers)
    destination_categories = get_component_categories(destination_domain, dest_headers)

    destination_categories_dict = {
        cat["referenceId"]: cat for cat in destination_categories
    }

    for source_cat in source_categories:
        reference_id = source_cat["referenceId"]
        if reference_id in destination_categories_dict:
            logging.info(f"Component category {reference_id} exists in destination, checking for updates")
            source_full_cat = get_component_category(
                source_domain, source_cat["id"], source_headers
            )
            destination_full_cat = get_component_category(
                destination_domain,
                destination_categories_dict[reference_id]["id"],
                dest_headers,
            )

            # Needs to be saved for PUT
            dest_cat_id = destination_full_cat["id"]

            # Need to delete to properly compare
            del source_full_cat["id"]
            del destination_full_cat["id"]
            del source_full_cat["_links"]
            del destination_full_cat["_links"]

            if source_full_cat != destination_full_cat:
                logging.info(f"Component category {reference_id} differs, updating destination")
                # This is the only field the user can change
                cat_to_put = {
                    "sharedWithAllUsers": source_full_cat["sharedWithAllUsers"],
                }
                update_component_category(
                    destination_domain,
                    dest_cat_id,
                    cat_to_put,
                    config.dest_head,
                )
        else:
            logging.info(f"Component category {reference_id} does not exist in destination, creating new category")
            source_full_cat = get_component_category(
                source_domain, source_cat["id"], source_headers
            )
            cat_to_post = {
                "name": source_full_cat["name"],
                "referenceId": source_full_cat["referenceId"],
            }
            create_component_category(destination_domain, cat_to_post, dest_headers)
    logging.info("tenant_config_migration_component_categories | END")


if __name__ == "__main__":
    main(config.source_domain, config.dest_domain, config.source_head, config.dest_head)

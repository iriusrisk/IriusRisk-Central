import requests
import config
import constants

SOURCE_DOMAIN = config.source_domain
DESTINATION_DOMAIN = config.dest_domain
SOURCE_HEADERS = config.source_head
DEST_HEADERS = config.dest_head
MAX_SIZE = "?size=10000"


def get_component_categories(domain, headers):
    response = requests.get(
        f"{domain}{constants.ENDPOINT_COMPONENTS_CATEGORIES_SUMMARY}{MAX_SIZE}",
        headers=headers,
    )
    response.raise_for_status()
    return response.json()["_embedded"]["items"]


def get_component_category(domain, category_id, headers):
    response = requests.get(
        f"{domain}{constants.ENDPOINT_COMPONENTS_CATEGORIES}/{category_id}{MAX_SIZE}",
        headers=headers,
    )
    response.raise_for_status()
    return response.json()


def update_component_category(domain, category_id, data, headers):
    response = requests.put(
        f"{domain}{constants.ENDPOINT_COMPONENTS_CATEGORIES}/{category_id}",
        headers=headers,
        json=data,
    )
    response.raise_for_status()
    return response.json()


def create_component_category(domain, data, headers):
    response = requests.post(
        f"{domain}{constants.ENDPOINT_COMPONENTS_CATEGORIES}",
        headers=headers,
        json=data,
    )
    response.raise_for_status()
    return response.json()


def migrate_component_categories():
    source_categories = get_component_categories(SOURCE_DOMAIN, SOURCE_HEADERS)
    destination_categories = get_component_categories(DESTINATION_DOMAIN, DEST_HEADERS)

    destination_categories_dict = {
        cat["referenceId"]: cat for cat in destination_categories
    }

    for source_cat in source_categories:
        reference_id = source_cat["referenceId"]
        if reference_id in destination_categories_dict:
            source_full_cat = get_component_category(
                SOURCE_DOMAIN, source_cat["id"], config.source_head
            )
            destination_full_cat = get_component_category(
                DESTINATION_DOMAIN,
                destination_categories_dict[reference_id]["id"],
                config.dest_head,
            )

            del source_full_cat["id"]
            del destination_full_cat["id"]
            del source_full_cat["_links"]
            del destination_full_cat["_links"]

            if source_full_cat != destination_full_cat:
                # This is the only field the user can change
                cat_to_put = {
                    "sharedWithAllUsers": source_full_cat["sharedWithAllUsers"],
                }
                update_component_category(
                    DESTINATION_DOMAIN,
                    destination_full_cat["id"],
                    cat_to_put,
                    config.dest_head,
                )
        else:
            source_full_cat = get_component_category(
                SOURCE_DOMAIN, source_cat["id"], config.source_head
            )
            cat_to_post = {
                "name": source_full_cat["name"],
                "referenceId": source_full_cat["referenceId"],
            }
            create_component_category(DESTINATION_DOMAIN, cat_to_post, config.dest_head)


if __name__ == "__main__":
    migrate_component_categories()

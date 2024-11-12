import pip._vendor.requests as requests
import sys
import config
import logging
import helper_functions
import constants
import mappers

# Set up logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

# -------------INITIALISE ENVIRONMENT-----------------#
sys.stdout.reconfigure(encoding="utf-8")


def map_category_ids(categories1, categories2):
    """Map category IDs between two domains based on category names."""
    ids_names_mapping = {}
    for item1 in categories1["_embedded"]["items"]:
        for item2 in categories2["_embedded"]["items"]:
            if item1["name"] == item2["name"]:
                ids_names_mapping[item1["name"]] = {
                    "id_from_api1": item1["id"],
                    "id_from_api2": item2["id"],
                }
    logging.info("Mapped category IDs between domains.")
    return ids_names_mapping


def post_component_to_domain(component, category_id, post_url, headers):
    """Post a component to the target domain."""
    myobj = {
        "referenceId": component["referenceId"],
        "name": component["name"],
        "description": component.get("description", ""),
        "category": {"id": category_id},
        "visible": component.get("visible", True),
    }

    response = helper_functions.post_request(myobj, post_url, headers)
    if response:
        logging.info(f"Posted component {component['name']} to domain 2.")
        return response["id"]


def get_risk_patterns_for_component(component_id, domain, headers):
    """Retrieve risk patterns for a specific component in a domain."""
    url = f"{domain}/api/v2/components/{component_id}/risk-patterns"
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        logging.info(f"Retrieved risk patterns for component {component_id}.")
        return response.json()["_embedded"]["items"]
    else:
        logging.error(
            f"Failed to retrieve risk patterns for component {component_id}. Status: {response.status_code}"
        )
        return []


def get_libraries(domain, headers):
    """Retrieve libraries from a domain."""
    url = f"{domain}/api/v2/libraries"
    return helper_functions.get_request(domain, constants.ENDPOINT_LIBRARIES, headers)


def get_risk_patterns_by_library(library_id, domain, headers):
    """Retrieve risk patterns by library ID in a domain."""
    url = f"{domain}/api/v2/libraries/{library_id}/risk-patterns"
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return {
            item["name"]: item["id"] for item in response.json()["_embedded"]["items"]
        }
    logging.error(
        f"Failed to retrieve risk patterns for library {library_id}. Status: {response.status_code}"
    )
    return {}


def associate_risk_patterns_with_component(
    component_id, risk_patterns, post_url, headers
):
    """Associate risk patterns with a component in the target domain."""
    for (risk_pattern_name, library_name), risk_pattern_id in risk_patterns.items():
        response = requests.post(
            f"{post_url}/api/v2/components/{component_id}/risk-patterns",
            headers=headers,
            json={"riskPattern": {"id": risk_pattern_id}},
        )
        if response.status_code in [200, 201]:
            logging.info(
                f"Associated risk pattern {risk_pattern_name} with component {component_id}."
            )
        else:
            logging.error(
                f"Failed to associate risk pattern {risk_pattern_name} with component {component_id}. Status: {response.status_code}"
            )


def process_components_and_associate_risk_patterns():
    """Main function to process components and associate risk patterns."""
    # Get all components from both domains
    data1 = helper_functions.get_request(
        config.start_domain,
        constants.ENDPOINT_COMPONENTS,
        config.start_head,
    )
    data2 = helper_functions.get_request(
        config.post_domain,
        constants.ENDPOINT_COMPONENTS,
        config.post_head,
    )

    # Get all component categories from both domains
    categories1 = helper_functions.get_request(
        config.start_domain,
        constants.ENDPOINT_COMPONENTS_CATEGORIES_SUMMARY,
        config.start_head,
    )
    categories2 = helper_functions.get_request(
        config.post_domain,
        constants.ENDPOINT_COMPONENTS_CATEGORIES_SUMMARY,
        config.post_head,
    )

    # Map category IDs
    ids_names_mapping = map_category_ids(categories1, categories2)

    matches = helper_functions.find_matches(
        data1["_embedded"]["items"], data2["_embedded"]["items"], "referenceId"
    )

    # Retrieve existing components from domain 2
    existing_components = {item["name"] for item in data2["_embedded"]["items"]}
    post_url = config.post_domain + constants.ENDPOINT_COMPONENTS

    # Process each component
    for component in data1["_embedded"]["items"]:
        component_has_been_put = False

        category_info = ids_names_mapping.get(component["category"]["name"], {})
        category_id = category_info.get("id_from_api2")
        if not category_id:
            logging.warning(
                f"Category ID for '{component['category']['name']}' not found. Skipping component {component['name']}."
            )
            continue

        component_id = None

        if component["name"] in existing_components:
            if (
                helper_functions.is_ir_object_same_keep_id(
                    component, data2["_embedded"]["items"]
                )
                is False
            ):
                uuid = matches[component["referenceId"]]
                component_to_put = mappers.map_component_to_put(component, category_id)
                helper_functions.put_request(
                    uuid,
                    component_to_put,
                    post_url,
                    config.post_head,
                )
                component_has_been_put = True
                component_id = uuid
                continue
            else:
                logging.info(f"Component [{component['name']}] is the same.")
                continue

        # Post component to domain 2

        if component_has_been_put is False:
            component_id = post_component_to_domain(
                component, category_id, post_url, config.post_head
            )
            if not component_id:
                continue

        # Get risk patterns for the component from domain 1
        risk_patterns_start = get_risk_patterns_for_component(
            component["id"], config.start_domain, config.start_head
        )

        # Create a mapping of risk pattern names and library names
        risk_patterns_by_name_start = {
            (rp["name"], rp["library"]["name"]): rp["id"] for rp in risk_patterns_start
        }

        # Get libraries from domain 2
        libraries_data = helper_functions.get_request(
            config.post_domain, constants.ENDPOINT_LIBRARIES, config.post_head
        )
        library_name_to_id_post = {
            item["name"]: item["id"] for item in libraries_data["_embedded"]["items"]
        }

        # Retrieve risk patterns for each library in domain 2
        risk_patterns_by_library_post = {}
        for library_name, library_id in library_name_to_id_post.items():
            risk_patterns_by_library_post[library_name] = get_risk_patterns_by_library(
                library_id, config.post_domain, config.post_head
            )

        # Map risk patterns from domain 1 to domain 2 and associate them
        risk_patterns_to_associate = {}
        for (
            risk_pattern_name,
            library_name,
        ), risk_pattern_id_start in risk_patterns_by_name_start.items():
            post_risk_pattern_id = risk_patterns_by_library_post.get(
                library_name, {}
            ).get(risk_pattern_name)
            if post_risk_pattern_id:
                risk_patterns_to_associate[(risk_pattern_name, library_name)] = (
                    post_risk_pattern_id
                )
            else:
                logging.warning(
                    f"No matching risk pattern found for {risk_pattern_name} in domain 2 for library {library_name}"
                )

        # Associate risk patterns with the new component in domain 2
        associate_risk_patterns_with_component(
            component_id,
            risk_patterns_to_associate,
            config.post_domain,
            config.post_head,
        )


if __name__ == "__main__":
    logging.info("tenant_config_migration_components | START")
    process_components_and_associate_risk_patterns()
    logging.info("tenant_config_migration_components | END")

import pip._vendor.requests as requests
import sys
import config
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# -------------INITIALISE ENVIRONMENT-----------------#
element_size = '?size=10000'
sys.stdout.reconfigure(encoding='utf-8')

def fetch_data(url, headers, description):
    """Fetch data from a given URL and log the result."""
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        logging.info(f"Successfully fetched {description}.")
        return response.json()
    logging.error(f"Failed to fetch {description}. Status: {response.status_code}")
    return None

def get_components(domain, headers, description):
    """Retrieve components from a domain."""
    url = f"{domain}/api/v2/components{element_size}"
    return fetch_data(url, headers, description)

def get_component_categories(domain, headers, description):
    """Retrieve component categories from a domain."""
    url = f"{domain}/api/v2/components/categories/summary{element_size}"
    return fetch_data(url, headers, description)

def map_category_ids(categories1, categories2):
    """Map category IDs between two domains based on category names."""
    ids_names_mapping = {}
    for item1 in categories1['_embedded']['items']:
        for item2 in categories2['_embedded']['items']:
            if item1['name'] == item2['name']:
                ids_names_mapping[item1['name']] = {
                    'id_from_api1': item1['id'],
                    'id_from_api2': item2['id']
                }
    logging.info("Mapped category IDs between domains.")
    return ids_names_mapping

def post_component_to_domain(component, category_id, post_url, headers):
    """Post a component to the target domain."""
    myobj = {
        "referenceId": component['referenceId'],
        "name": component['name'],
        "description": component.get('description', ''),
        "category": {
            "id": category_id
        },
        "visible": component.get('visible', True)
    }

    response = requests.post(post_url, headers=headers, json=myobj)
    
    if response.status_code in [200, 201]:
        logging.info(f"Successfully posted component: {component['name']}")
        return response.json()['id']
    else:
        logging.error(f"Failed to post component: {component['name']}. Status: {response.status_code}, Response: {response.text}")
        return None

def get_risk_patterns_for_component(component_id, domain, headers):
    """Retrieve risk patterns for a specific component in a domain."""
    url = f"{domain}/api/v2/components/{component_id}/risk-patterns"
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        logging.info(f"Retrieved risk patterns for component {component_id}.")
        return response.json()['_embedded']['items']
    else:
        logging.error(f"Failed to retrieve risk patterns for component {component_id}. Status: {response.status_code}")
        return []

def get_libraries(domain, headers):
    """Retrieve libraries from a domain."""
    url = f"{domain}/api/v2/libraries"
    return fetch_data(url, headers, "libraries")

def get_risk_patterns_by_library(library_id, domain, headers):
    """Retrieve risk patterns by library ID in a domain."""
    url = f"{domain}/api/v2/libraries/{library_id}/risk-patterns"
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return {item['name']: item['id'] for item in response.json()['_embedded']['items']}
    logging.error(f"Failed to retrieve risk patterns for library {library_id}. Status: {response.status_code}")
    return {}

def associate_risk_patterns_with_component(component_id, risk_patterns, post_url, headers):
    """Associate risk patterns with a component in the target domain."""
    for (risk_pattern_name, library_name), risk_pattern_id in risk_patterns.items():
        response = requests.post(
            f"{post_url}/api/v2/components/{component_id}/risk-patterns",
            headers=headers,
            json={"riskPattern": {"id": risk_pattern_id}}
        )
        if response.status_code in [200, 201]:
            logging.info(f"Associated risk pattern {risk_pattern_name} with component {component_id}.")
        else:
            logging.error(f"Failed to associate risk pattern {risk_pattern_name} with component {component_id}. Status: {response.status_code}")

def process_components_and_associate_risk_patterns():
    """Main function to process components and associate risk patterns."""
    # Get all components from both domains
    data1 = get_components(config.start_domain, config.start_head, "components from domain 1")
    data2 = get_components(config.post_domain, config.post_head, "components from domain 2")

    # Get all component categories from both domains
    categories1 = get_component_categories(config.start_domain, config.start_head, "categories from domain 1")
    categories2 = get_component_categories(config.post_domain, config.post_head, "categories from domain 2")

    # Map category IDs
    ids_names_mapping = map_category_ids(categories1, categories2)

    # Retrieve existing components from domain 2
    existing_components = {item['name'] for item in data2['_embedded']['items']}
    post_url = f"{config.post_domain}/api/v2/components"

    # Process each component
    for component in data1['_embedded']['items']:
        component_name = component['name']
        if component_name in existing_components:
            # Removed logging for existing components to reduce noise
            continue

        category_info = ids_names_mapping.get(component['category']['name'], {})
        category_id = category_info.get('id_from_api2')
        if not category_id:
            logging.warning(f"Category ID for '{component['category']['name']}' not found. Skipping component {component_name}.")
            continue

        # Post component to domain 2
        new_component_id = post_component_to_domain(component, category_id, post_url, config.post_head)
        if not new_component_id:
            continue

        # Get risk patterns for the component from domain 1
        risk_patterns_start = get_risk_patterns_for_component(component['id'], config.start_domain, config.start_head)

        # Create a mapping of risk pattern names and library names
        risk_patterns_by_name_start = {
            (rp['name'], rp['library']['name']): rp['id'] for rp in risk_patterns_start
        }

        # Get libraries from domain 2
        libraries_data = get_libraries(config.post_domain, config.post_head)
        library_name_to_id_post = {item['name']: item['id'] for item in libraries_data['_embedded']['items']}

        # Retrieve risk patterns for each library in domain 2
        risk_patterns_by_library_post = {}
        for library_name, library_id in library_name_to_id_post.items():
            risk_patterns_by_library_post[library_name] = get_risk_patterns_by_library(library_id, config.post_domain, config.post_head)

        # Map risk patterns from domain 1 to domain 2 and associate them
        risk_patterns_to_associate = {}
        for (risk_pattern_name, library_name), risk_pattern_id_start in risk_patterns_by_name_start.items():
            post_risk_pattern_id = risk_patterns_by_library_post.get(library_name, {}).get(risk_pattern_name)
            if post_risk_pattern_id:
                risk_patterns_to_associate[(risk_pattern_name, library_name)] = post_risk_pattern_id
            else:
                logging.warning(f"No matching risk pattern found for {risk_pattern_name} in domain 2 for library {library_name}")

        # Associate risk patterns with the new component in domain 2
        associate_risk_patterns_with_component(new_component_id, risk_patterns_to_associate, config.post_domain, config.post_head)

if __name__ == "__main__":
    process_components_and_associate_risk_patterns()

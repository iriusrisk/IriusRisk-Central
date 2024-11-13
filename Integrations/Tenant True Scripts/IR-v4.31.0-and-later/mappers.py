# Mappers from JSON to Irius Risk objects

# Security Classifications Mapper
def map_security_classifications(data):
    items = []

    for item in data["_embedded"]["items"]:
        item_data = {
            "id": item["id"],
            "referenceId": item["referenceId"],
            "name": item["name"],
            "description": item["description"],
            "confidentiality": item["confidentiality"],
            "integrity": item["integrity"],
            "availability": item["availability"],
        }
        items.append(item_data)
    return items


# Assets Mapper
def map_assets(data):
    items = []
    for item in data["_embedded"]["items"]:
        item_data = {
            "id": item["id"],
            "name": item["name"],
            "description": item["description"],
            "securityClassification": item["securityClassification"],
        }
        items.append(item_data)
    return items


# Business Units Mapper
def map_business_units(data):
    items = []
    for item in data["_embedded"]["items"]:
        item_data = {
            "id": item["id"],
            "referenceId": item["referenceId"],
            "name": item["name"],
            "description": item["description"],
        }
        items.append(item_data)
    return items


def map_custom_fields(data, type_ids_mapping):
    items = []

    for item in data["_embedded"]["items"]:
        item_data = {
            "id": item["id"],
            "name": item["name"],
            "description": item["description"],
            "referenceId": item["referenceId"],
            "entity": item["entity"],
            "required": item["required"],
            "visible": item["visible"],
            "editable": item["editable"],
            "exportable": item["exportable"],
            "defaultValue": item["defaultValue"],
            "maxSize": item["maxSize"],
            "regexValidator": item["regexValidator"],
            "typeId": item["type"]["id"],
        }
        items.append(item_data)

    return items


def map_single_custom_field(item, type_ids_mapping):
    item_data = {
        "id": item["id"],
        "name": item["name"],
        "description": item["description"],
        "referenceId": item["referenceId"],
        "entity": item["entity"],
        "required": item["required"],
        "visible": item["visible"],
        "editable": item["editable"],
        "exportable": item["exportable"],
        "defaultValue": item["defaultValue"],
        "maxSize": item["maxSize"],
        "regexValidator": item["regexValidator"],
        "typeId": type_ids_mapping[item["type"]["id"]],
    }

    return item_data


def map_trust_zones(data):
    items = []
    for item in data["_embedded"]["items"]:
        item_data = {
            "id": item["id"],
            "referenceId": item["referenceId"],
            "name": item["name"],
            "description": item["description"],
            "trustRating": item["trustRating"],
            # TODO Check this
            "sharedWithAllUsers": item["defaultTrustZone"],
        }
        items.append(item_data)
    return items


def map_libraries(data):
    items = []
    for item in data["_embedded"]["items"]:
        if item.get("type", "").lower() == "custom":
            item_data = {
                "id": item["id"],
                "referenceId": item["referenceId"],
                "name": item["name"],
                "description": item["description"],
                "tags": item["tags"],
            }
            items.append(item_data)
    return items


def map_component_to_put(data, category_id):
    return {
        "category": {
            "id": category_id,
        },
        "name": data["name"],
        "description": data["description"],
        "visible": data.get("visible", True),
    }

def map_roles(data):
    mapped_roles = []
    for item in data['_embedded']['items']:
        mapped_roles.append({
            'id': item['id'],
            'name': item['name'],
            'description': item.get('description', ''),
        })
    return mapped_roles
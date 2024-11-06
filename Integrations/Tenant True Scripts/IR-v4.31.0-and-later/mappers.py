def map_security_classifications(data):
    roles = []

    for role in data["_embedded"]["items"]:
        role_data = {
            "id": role["id"],
            "referenceId": role["referenceId"],
            "name": role["name"],
            "description": role["description"],
            "confidentiality": role["confidentiality"],
            "integrity": role["integrity"],
            "availability": role["availability"],
        }
        roles.append(role_data)
    return roles


def map_assets(data):
    items = []
    for item in data["_embedded"]["items"]:
        role_data = {
            "id": item["id"],
            "name": item["name"],
            "description": item["description"],
            "securityClassification": item["securityClassification"],
        }
        items.append(role_data)
    return items

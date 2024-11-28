import config
import constants
import helper_functions
import logging

source_library_endpoint = config.source_domain + constants.ENDPOINT_LIBRARIES
dest_library_endpoint = config.dest_domain + constants.ENDPOINT_LIBRARIES

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


def find_matching_libraries(all_source_libraries, all_dest_libraries):
    matches = helper_functions.find_matches(
        all_source_libraries["_embedded"]["items"],
        all_dest_libraries["_embedded"]["items"],
        "referenceId",
    )

    return matches


all_source_libraries = helper_functions.get_request(
    config.source_domain, constants.ENDPOINT_LIBRARIES, config.source_head
)
all_dest_libraries = helper_functions.get_request(
    config.dest_domain, constants.ENDPOINT_LIBRARIES, config.dest_head
)


def migrate_libraries():
    all_source_libraries["_embedded"]["items"] = [
        library
        for library in all_source_libraries["_embedded"]["items"]
        if library["type"] == "custom"
    ]

    all_dest_libraries["_embedded"]["items"] = [
        library
        for library in all_dest_libraries["_embedded"]["items"]
        if library["type"] == "custom"
    ]

    matching_libraries = find_matching_libraries(
        all_source_libraries, all_dest_libraries
    )

    for library in all_source_libraries["_embedded"]["items"]:
        library_id = None
        if library["referenceId"] in matching_libraries:
            logging.info(f"Library {library['name']} already exists in destination")

            library_to_put = {
                "name": library["name"],
                "description": library["description"],
                "tags": library["tags"],
            }

            print(library_to_put)

            response = helper_functions.put_request(
                matching_libraries[library["referenceId"]],
                library_to_put,
                dest_library_endpoint,
                config.dest_head,
            )
            logging.info(f"Response: {response}")
            library_id = response["id"]
        else:
            library_to_post = {
                "name": library["name"],
                "description": library["description"],
                "referenceId": library["referenceId"],
                "tags": library["tags"],
            }

            print(library_to_post)

            response = helper_functions.post_request(
                library_to_post, dest_library_endpoint, config.dest_head
            )
            logging.info(f"Response: {response}")
            library_id = response["id"]

        risk_pattern_id = migrate_risk_patterns(library["id"], library_id)
        migrate_weaknesses(all_source_libraries)
        migrate_countermeasure(library["id"], library_id, risk_pattern_id)


def migrate_risk_patterns(source_library_id, dest_library_id):
    source_risk_patterns = helper_functions.get_request(
        f"{source_library_endpoint}/{source_library_id}/risk-patterns",
        "",
        config.source_head,
    )

    dest_risk_patterns = helper_functions.get_request(
        f"{dest_library_endpoint}/{dest_library_id}/risk-patterns",
        "",
        config.dest_head,
    )

    matching_risk_patterns = helper_functions.find_matches(
        source_risk_patterns["_embedded"]["items"],
        dest_risk_patterns["_embedded"]["items"],
        "referenceId",
    )

    for risk_pattern in source_risk_patterns["_embedded"]["items"]:
        if risk_pattern["referenceId"] in matching_risk_patterns:
            logging.info(
                f"Risk Pattern {risk_pattern['name']} already exists in destination"
            )

            risk_pattern_to_put = {
                "name": risk_pattern["name"],
                "referenceId": risk_pattern["referenceId"],
                "description": risk_pattern["description"],
                "tags": risk_pattern["tags"],
            }

            response = helper_functions.put_request(
                matching_risk_patterns[risk_pattern["referenceId"]],
                risk_pattern_to_put,
                f"{dest_library_endpoint}/risk-patterns",
                config.dest_head,
            )

            logging.info(f"Response: {response}")
        else:
            logging.info(f"Creating Risk Pattern {risk_pattern['name']}")

            risk_pattern_to_post = {
                "library": {"id": dest_library_id},
                "name": risk_pattern["name"],
                "description": risk_pattern["description"],
                "referenceId": risk_pattern["referenceId"],
                "tags": risk_pattern["tags"],
            }

            response = helper_functions.post_request(
                risk_pattern_to_post,
                f"{dest_library_endpoint}/risk-patterns",
                config.dest_head,
            )

            logging.info(f"Response: {response}")

        migrate_use_cases(
            source_library_id, dest_library_id, risk_pattern["id"], response["id"]
        )

        return response["id"]


def migrate_use_cases(
    source_library_id, dest_library_id, source_risk_pattern_id, dest_risk_pattern_id
):
    source_use_cases = helper_functions.get_request(
        f"{source_library_endpoint}/risk-patterns/{source_risk_pattern_id}/use-cases",
        "",
        config.source_head,
    )

    dest_use_cases = helper_functions.get_request(
        f"{dest_library_endpoint}/risk-patterns/{dest_risk_pattern_id}/use-cases",
        "",
        config.dest_head,
    )

    matching_use_cases = helper_functions.find_matches(
        source_use_cases["_embedded"]["items"],
        dest_use_cases["_embedded"]["items"],
        "referenceId",
    )

    for use_case in source_use_cases["_embedded"]["items"]:
        if use_case["referenceId"] in matching_use_cases:
            logging.info(f"Use Case {use_case['name']} already exists in destination")

            use_case_to_put = {
                "name": use_case["name"],
                "description": use_case["description"],
            }

            response = helper_functions.put_request(
                matching_use_cases[use_case["referenceId"]],
                use_case_to_put,
                f"{dest_library_endpoint}/use-cases",
                config.dest_head,
            )

            logging.info(f"Response: {response}")
        else:
            logging.info(f"Creating Use Case {use_case['name']}")

            use_case_to_post = {
                "riskPattern": {"id": dest_risk_pattern_id},
                "name": use_case["name"],
                "description": use_case["description"],
                "referenceId": use_case["referenceId"],
            }

            response = helper_functions.post_request(
                use_case_to_post,
                f"{dest_library_endpoint}/use-cases",
                config.dest_head,
            )

            logging.info(f"Response: {response}")

        if response:
            migrate_threats(source_library_id, dest_library_id, response["id"])


def migrate_threats(source_library_id, dest_library_id, usecase_id):
    source_threats = helper_functions.get_request(
        f"{source_library_endpoint}/{source_library_id}/threats/summary",
        "",
        config.source_head,
    )

    dest_threats = helper_functions.get_request(
        f"{dest_library_endpoint}/{dest_library_id}/threats/summary",
        "",
        config.dest_head,
    )

    matching_threats = helper_functions.find_matches(
        source_threats["_embedded"]["items"],
        dest_threats["_embedded"]["items"],
        "referenceId",
    )

    for threat in source_threats["_embedded"]["items"]:
        if threat["referenceId"] in matching_threats:
            logging.info(f"Threat {threat['name']} already exists in destination")

            threat = helper_functions.get_request(
                f"{source_library_endpoint}/threats/{threat['id']}",
                "",
                config.source_head,
            )

            threat_to_put = {
                "name": threat["name"],
                "description": threat["description"],
            }

            response = helper_functions.put_request(
                matching_threats[threat["referenceId"]],
                threat_to_put,
                f"{dest_library_endpoint}/threats/{threat['id']}",
                config.dest_head,
            )

            logging.info(f"Response: {response}")
        else:
            logging.info(f"Creating Threat {threat['name']}")

            threat = helper_functions.get_request(
                f"{source_library_endpoint}/threats/{threat['id']}",
                "",
                config.source_head,
            )

            threat_to_post = {
                "availability": "100",
                "confidentiality": "100",
                "easeOfExploitation": "25",
                "integrity": "100",
                "name": threat["name"],
                "referenceId": threat["referenceId"],
                "useCase": {"id": usecase_id},
                "description": threat["description"],
                "customFields": get_dest_custom_fields("threat"),
            }

            response = helper_functions.post_request(
                threat_to_post,
                f"{dest_library_endpoint}/threats",
                config.dest_head,
            )

            logging.info(f"Response: {response}")


def map_custom_fields(custom_fields):
    source_custom_fields = helper_functions.get_request(
        f"{config.source_domain}",
        constants.ENDPOINT_CUSTOM_FIELDS,
        config.source_head,
    )

    dest_custom_fields = helper_functions.get_request(
        f"{config.dest_domain}",
        constants.ENDPOINT_CUSTOM_FIELDS,
        config.dest_head,
    )

    matching_custom_fields = helper_functions.find_matches(
        source_custom_fields["_embedded"]["items"],
        dest_custom_fields["_embedded"]["items"],
        "name",
    )

    custom_fields_to_return = []

    for custom_field in custom_fields:
        if custom_field["customField"]["name"] in matching_custom_fields:
            logging.info(
                f"Custom Field {custom_field['customField']['name']} already exists in destination"
            )

            custom_fields_to_return.append(
                {
                    "customField": {
                        "id": matching_custom_fields[
                            custom_field["customField"]["name"]
                        ]
                    },
                    "value": custom_field["value"],
                }
            )
        else:
            logging.info(f"Creating Custom Field {custom_field['name']}")

            custom_field = helper_functions.get_request(
                f"{config.source_domain}/custom-fields/{custom_field['id']}",
                "",
                config.source_head,
            )

            custom_fields_to_post = {
                "entity": custom_field["entity"],
                "name": custom_field["name"],
                "referenceId": custom_field["referenceId"],
                "typeId": custom_field["typeId"],
                "description": custom_field["description"],
                "required": custom_field["required"],
                "visible": custom_field["visible"],
                "editable": custom_field["editable"],
                "exportable": custom_field["exportable"],
                "defaultValue": custom_field["defaultValue"],
                "maxSize": custom_field["maxSize"],
                "regexValidator": custom_field["regexValidator"],
                "groupId": custom_field["groupId"],
                "after": custom_field["after"],
            }

            response = helper_functions.post_request(
                custom_fields_to_post,
                f"{config.dest_domain}{constants.ENDPOINT_CUSTOM_FIELDS}",
                config.dest_head,
            )

            logging.info(f"Response: {response}")

            custom_fields_to_return.append(
                {
                    "customField": {"id": custom_field["id"]},
                    "value": custom_field["customField"]["value"],
                }
            )

    return custom_fields_to_return


def migrate_weaknesses(all_source_libraries):
    source_waeknesses = helper_functions.get_request(
        f"{source_library_endpoint}/weaknesses",
        "",
        config.source_head,
    )
    dest_weaknesses = helper_functions.get_request(
        f"{dest_library_endpoint}/weaknesses",
        "",
        config.dest_head,
    )

    matching_weaknesses = helper_functions.find_matches(
        source_waeknesses["_embedded"]["items"],
        dest_weaknesses["_embedded"]["items"],
        "referenceId",
    )

    for weakness in source_waeknesses["_embedded"]["items"]:
        if (
            weakness["library"]["id"] in all_source_libraries
        ):  # check if library is custom
            if weakness["referenceId"] in matching_weaknesses:
                logging.info(
                    f"Weakness {weakness['name']} already exists in destination"
                )

                weakness_to_put = {
                    "name": weakness["name"],
                    "description": weakness["description"],
                    "impact": weakness["impact"],
                    "referenceId": weakness["referenceId"],
                }

                response = helper_functions.put_request(
                    matching_weaknesses[weakness["referenceId"]],
                    weakness_to_put,
                    f"{dest_library_endpoint}/weaknesses",
                    config.dest_head,
                )

                logging.info(f"Response: {response}")
            else:
                logging.info(f"Creating Weakness {weakness['name']}")

                weakness_to_post = {
                    "impact": weakness["impact"],
                    "name": weakness["name"],
                    "description": weakness["description"],
                    "referenceId": weakness["referenceId"],
                    "riskPattern": {"id": weakness["riskPattern"]["id"]},
                }

                response = helper_functions.post_request(
                    weakness_to_post,
                    f"{dest_library_endpoint}/weaknesses",
                    config.dest_head,
                )

                logging.info(f"Response: {response}")


def migrate_countermeasure(source_library_id, dest_library_id, risk_pattern_id):
    source_countermeasures_summary = helper_functions.get_request(
        f"{source_library_endpoint}/{source_library_id}/countermeasures/summary",
        "",
        config.source_head,
    )
    dest_countermeasures_summary = helper_functions.get_request(
        f"{dest_library_endpoint}/{dest_library_id}/countermeasures/summary",
        "",
        config.dest_head,
    )

    matching_countermeasures = helper_functions.find_matches(
        source_countermeasures_summary["_embedded"]["items"],
        dest_countermeasures_summary["_embedded"]["items"],
        "referenceId",
    )

    for countermeasure in source_countermeasures_summary["_embedded"]["items"]:
        if countermeasure["referenceId"] in matching_countermeasures:
            logging.info(
                f"Countermeasure {countermeasure['name']} already exists in destination"
            )

            countermeasure = helper_functions.get_request(
                f"{source_library_endpoint}/countermeasures/{countermeasure['id']}",
                "",
                config.source_head,
            )

            countermeasure_to_put = {
                "cost": countermeasure["cost"],
                "name": countermeasure["name"],
                "referenceId": countermeasure["referenceId"],
                "riskPattern": {"id": risk_pattern_id},
                "state": countermeasure["state"],
                "description": countermeasure["description"],
                "customFields": get_dest_custom_fields("countermeasure"),
            }

            response = helper_functions.put_request(
                matching_countermeasures[countermeasure["referenceId"]],
                countermeasure_to_put,
                f"{dest_library_endpoint}/countermeasures",
                config.dest_head,
            )

            logging.info(f"Response: {response}")
        else:
            logging.info(f"Creating Countermeasure {countermeasure['name']}")

            countermeasure = helper_functions.get_request(
                f"{source_library_endpoint}/countermeasures/{countermeasure['id']}",
                "",
                config.source_head,
            )

            countermeasure_to_post = {
                "cost": countermeasure["cost"],
                "name": countermeasure["name"],
                "referenceId": countermeasure["referenceId"],
                "riskPattern": {"id": risk_pattern_id},
                "state": countermeasure["state"],
                "description": countermeasure["description"],
                "customFields": get_dest_custom_fields("countermeasure"),
            }

            response = helper_functions.post_request(
                countermeasure_to_post,
                f"{dest_library_endpoint}/countermeasures",
                config.dest_head,
            )

            logging.info(f"Response: {response}")


def get_dest_custom_fields(value):
    headers = {"Accept": "application/hal+json", "api-token": config.dest_apitoken}
    response = helper_functions.get_request(
        config.dest_domain, constants.ENDPOINT_CUSTOM_FIELDS, headers
    )
    custom_fields_to_return = [
        {"customField": {"id": custom_field["id"]}, "value": None}
        for custom_field in response["_embedded"]["items"]
        if custom_field["entity"] == value
    ]
    return custom_fields_to_return


if __name__ == "__main__":
    library_id = migrate_libraries()

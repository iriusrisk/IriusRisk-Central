import json
import requests
import logging
import config
import constants
import helper_functions
import pandas as pd

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def get_dest_custom_fields(value):
    headers = {"Accept": "application/hal+json", "api-token": config.dest_apitoken}
    response = helper_functions.get_request(config.dest_domain, constants.ENDPOINT_CUSTOM_FIELDS, headers)
    custom_fields_to_return = [
        {"customField": {"id": custom_field["id"]}, "value": None}
        for custom_field in response["_embedded"]["items"]
        if custom_field["entity"] == value
    ]
    return custom_fields_to_return

def handle_library(library, library_ref, headers):
    library_data = json.dumps({"referenceId": library_ref, "name": library, "description": ""})
    response = requests.post(config.dest_domain + constants.ENDPOINT_LIBRARIES, headers=headers, data=library_data)
    if response.status_code == 200:
        logging.info("Library was created")
        logging.info(f"Library ID: {response.json()['id']}")
        return response.json()["id"]
    else:
        logging.error("Library was not created")
        return None

def handle_risk_pattern(risk_pattern, library_id, headers):
    riskpattern_endpoint = f"{config.dest_domain}{constants.ENDPOINT_LIBRARIES}/risk-patterns"
    payload = json.dumps({
        "library": {"id": library_id},
        "name": risk_pattern,
        "referenceId": risk_pattern.replace(" ", ""),
        "description": ""
    })
    response = requests.post(riskpattern_endpoint, headers=headers, data=payload)
    logging.info(f"Risk Pattern creation response: {response.status_code}")
    return response.json().get("id")

def handle_use_case(use_case, risk_pattern_id, headers):
    usecase_endpoint = f"{config.dest_domain}{constants.ENDPOINT_LIBRARIES}/use-cases"
    usecase_ref = helper_functions.create_and_verify_reference_id(use_case)
    usecase_data = json.dumps({
        "name": use_case,
        "referenceId": usecase_ref,
        "riskPattern": {"id": risk_pattern_id},
        "description": ""
    })
    response = requests.post(usecase_endpoint, headers=headers, data=usecase_data)
    logging.info(f"Use Case creation response: {response.status_code}")
    return response.json().get("id")

def handle_threat(threat, threat_desc, usecase_id, headers):
    threat_endpoint = f"{config.dest_domain}{constants.ENDPOINT_LIBRARIES}/threats"
    threat_ref = helper_functions.create_and_verify_reference_id(threat)
    custom_fields = get_dest_custom_fields("threat")
    threat_data = json.dumps({
        "availability": "100",
        "confidentiality": "100",
        "easeOfExploitation": "25",
        "integrity": "100",
        "name": threat,
        "referenceId": threat_ref,
        "useCase": {"id": usecase_id},
        "description": threat_desc,
        "customFields": custom_fields
    })
    response = requests.post(threat_endpoint, headers=headers, data=threat_data)
    logging.info(f"Threat creation response: {response.status_code}")
    logging.info(f"Threat ID: {response.json()['id']}")

def handle_weakness(weakness, risk_pattern_id, headers):
    weakness_ref = helper_functions.create_and_verify_reference_id(weakness)
    weakness_creation_endpoint = f"{config.dest_domain}{constants.ENDPOINT_LIBRARIES}/weaknesses"
    weakness_data = json.dumps({
        "impact": "50",
        "name": weakness,
        "referenceId": weakness_ref,
        "riskPattern": {"id": risk_pattern_id},
        "description": ""
    })
    response = requests.post(weakness_creation_endpoint, headers=headers, data=weakness_data)
    logging.info(f"Weakness creation response: {response.status_code}")
    logging.info(f"Weakness ID: {response.json()['id']}")

def handle_countermeasure(countermeasure, countermeasure_desc, risk_pattern_id, headers):
    countermeasure_creation_endpoint = f"{config.dest_domain}{constants.ENDPOINT_LIBRARIES}/countermeasures"
    countermeasure_ref = helper_functions.create_and_verify_reference_id(countermeasure)
    custom_fields = get_dest_custom_fields("countermeasure")
    countermeasure_data = json.dumps({
        "cost": "medium",
        "name": countermeasure,
        "referenceId": countermeasure_ref,
        "riskPattern": {"id": risk_pattern_id},
        "state": "required",
        "description": countermeasure_desc,
        "customFields": custom_fields
    })
    response = requests.post(countermeasure_creation_endpoint, headers=headers, data=countermeasure_data)
    logging.info(f"Countermeasure creation response: {response.status_code}")
    logging.info(f"Countermeasure ID: {response.json()['id']}")

def handle_standards(standardname, headers):
    standard_creation_endpoint = f"{config.dest_domain}/api/v2/standards"
    standard_ref = helper_functions.create_and_verify_reference_id(standardname)
    standard_data = json.dumps({
        "name": standardname,
        "referenceId": standard_ref
    })
    response = requests.post(standard_creation_endpoint, headers=headers, data=standard_data)
    logging.info(f"Standard creation response: {response.status_code}")
    if response.status_code == 200:
        logging.info(f"Standard ID: {response.json()['id']}")
        return response.json().get("id")
    elif response.status_code == 400:
        logging.error(f"Standard creation failed: {response.json()}")
        standards = helper_functions.get_request(config.dest_domain, constants.ENDPOINT_STANDARDS, headers)
        for standard in standards["_embedded"]["items"]:
            if standard["referenceId"] == standard_ref:
                return standard["id"]

def associate_standard(standard_id, suppstandref, headers):
    if suppstandref :
      associate_standard_endpoint = f"{config.dest_domain}{constants.ENDPOINT_LIBRARIES}/standard-references/{standard_id}"
      data = json.dumps({"reference": suppstandref, "standard": {"id": standard_id}})
      response = requests.put(associate_standard_endpoint, headers=headers, data=data)
      logging.info(f"Standard association response: {response.status_code}")

def library_creation(library, riskpattern, usecase, threat, threat_desc, weakness, countermeasure, countermeasure_desc, standardref, standardname, suppstandref):
    library_ref = helper_functions.create_and_verify_reference_id(library)
    
    headers = {"Content-Type": "application/json", "api-token": config.dest_apitoken}

    library_id = handle_library(library, library_ref, headers)
    if not library_id:
        return

    risk_pattern_id = handle_risk_pattern(riskpattern, library_id, headers)
    use_case_id = handle_use_case(usecase, risk_pattern_id, headers)
    handle_threat(threat, threat_desc, use_case_id, headers)
    handle_weakness(weakness, risk_pattern_id, headers)
    handle_countermeasure(countermeasure, countermeasure_desc, risk_pattern_id, headers)
    standard_id = handle_standards(standardname, headers)
    associate_standard(standard_id, suppstandref, headers)

if __name__ == "__main__":
    
    path = input("Enter the path of the Excel file: ")

    library_data = pd.read_excel(path)

    for index, row in library_data.iterrows():
        library_creation(
            row["Library"],
            row["Risk_Pattern"],
            row["Use_Case"],
            row["Threat"],
            row["Threat_Desc"],
            row["Weakness"],
            row["CM"],
            row["CM_Desc"],
            row["standardref"],
            row["standardname"],
            row["supported standardref"],
        )
        logging.info(f"Row {index + 1} Complete\n")

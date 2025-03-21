import requests
import json
import pandas as pd
import time
import logging
import os
import csv
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("library_creator.log"),
        logging.StreamHandler(),
    ],
)


class APICache:
    def __init__(self):
        self.cache = {
            "libraries": set(),
            "riskpatterns": set(),
            "usecases": set(),
            "threats": set(),
            "weaknesses": set(),
            "countermeasures": set(),
        }

    def exists(self, category, key):
        return key in self.cache[category]

    def add(self, category, key):
        self.cache[category].add(key)


cache = APICache()

summary = {
    "created": [],
    "skipped": [],
    "failed": [],
}

structure_preview = {}


def api_request(
    method, url, headers, data=None, expected_status=(200, 201), retries=3
):
    for attempt in range(retries):
        response = requests.request(method, url, headers=headers, data=data)

        if response.status_code in expected_status:
            return response

        if response.status_code == 400:
            error_text = response.text
            if "already exists" in error_text or "exists" in error_text:
                return "exists"

        if response.status_code in [404, 405, 409]:
            logging.warning(f"{response.status_code} Error: {response.text}")
            return None

        logging.error(
            f"Attempt {attempt + 1}/{retries} failed for {url} - {response.text}"
        )
        time.sleep(2)
    return None


def exists_via_get(full_url, headers):
    response = requests.get(full_url, headers=headers)
    return response.status_code == 200


def is_blank(value):
    return pd.isna(value) or str(value).strip().lower() in ["", "nan"]


def record_summary(status, entity_type, ref):
    summary[status].append((entity_type, ref))


def update_structure(library, rp, uc, threat, weakness, countermeasure):
    structure_preview.setdefault(library, {}).setdefault(rp, {}).setdefault(
        uc, {}
    ).setdefault(threat, {"weakness": weakness, "countermeasures": []})
    if weakness:
        structure_preview[library][rp][uc][threat]["weakness"] = weakness
    if countermeasure:
        structure_preview[library][rp][uc][threat]["countermeasures"].append(
            countermeasure
        )


def print_structure(structure):
    print("\n📦 Structure Preview\n")
    for library, patterns in structure.items():
        print(f"Library: {library}")
        for rp, usecases in patterns.items():
            print(f"  └─ Risk Pattern: {rp}")
            for uc, threats in usecases.items():
                print(f"     └─ Use Case: {uc}")
                for threat, items in threats.items():
                    print(f"        ├─ Threat: {threat}")
                    if items.get("weakness"):
                        print(f"        │   ├─ Weakness: {items['weakness']}")
                    if items.get("countermeasures"):
                        print(f"        │   └─ Countermeasures:")
                        for cm in items["countermeasures"]:
                            print(f"        │       └─ {cm}")


def build_structure_preview(library_data):
    for index, row in library_data.iterrows():
        update_structure(
            row["Library"],
            row["Risk_Pattern"],
            row["Use_Case"],
            row["Threat"] if not is_blank(row["Threat"]) else None,
            row["Weakness"] if not is_blank(row["Weakness"]) else None,
            row["CM"] if not is_blank(row["CM"]) else None,
        )


def library_creation(
    library,
    riskpattern,
    usecase,
    threat,
    threat_desc,
    weakness,
    countermeasure,
    countermeasure_desc,
    standardref,
    standardname,
    suppstandref,
):
    api_endpoint = os.getenv("IRIUSRISK_API_URL") + "/api/v1"
    api_token = os.getenv("IRIUSRISK_API_TOKEN")

    if not api_endpoint or not api_token:
        logging.error(
            "Missing IRIUSRISK_API_URL or IRIUSRISK_API_TOKEN environment variable."
        )
        exit(1)

    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "API-token": api_token,
    }

    if is_blank(library) or is_blank(riskpattern) or is_blank(usecase):
        logging.info(
            "Skipped row due to missing required fields (Library, Risk Pattern, or Use Case)."
        )
        return

    library_ref = str(library).replace(" ", "-")
    riskpattern_ref = str(riskpattern).replace(" ", "")
    usecase_ref = str(usecase).replace(" ", "-")
    threat_ref = str(threat).replace(" ", "-") if not is_blank(threat) else None
    weakness_ref = (
        str(weakness).replace(" ", "-") if not is_blank(weakness) else None
    )
    countermeasure_ref = (
        str(countermeasure).replace(" ", "_")
        if not is_blank(countermeasure)
        else None
    )

    library_url = f"{api_endpoint}/libraries/{library_ref}"
    if not cache.exists("libraries", library_ref):
        if exists_via_get(library_url, headers):
            logging.info(
                f"Library '{library}' already exists (GET confirmed). Skipping creation."
            )
            cache.add("libraries", library_ref)
        else:
            library_data = json.dumps(
                {"ref": library_ref, "name": library, "desc": ""}
            )
            response = api_request(
                "POST", f"{api_endpoint}/libraries", headers, library_data
            )
            if response:
                cache.add("libraries", library_ref)
                logging.info(f"Created Library: {library}")

    riskpattern_url = (
        f"{api_endpoint}/libraries/{library_ref}/riskpatterns/{riskpattern_ref}"
    )
    if not cache.exists("riskpatterns", riskpattern_ref):
        if exists_via_get(riskpattern_url, headers):
            logging.info(
                f"Risk Pattern '{riskpattern}' already exists. Skipping."
            )
            cache.add("riskpatterns", riskpattern_ref)
        else:
            riskpattern_data = json.dumps(
                {"ref": riskpattern_ref, "name": riskpattern, "desc": ""}
            )
            response = api_request(
                "POST",
                f"{api_endpoint}/libraries/{library_ref}/riskpatterns",
                headers,
                riskpattern_data,
            )
            if response:
                cache.add("riskpatterns", riskpattern_ref)
                logging.info(f"Created Risk Pattern: {riskpattern}")

    if not cache.exists("usecases", usecase_ref):
        usecase_data = json.dumps(
            {"ref": usecase_ref, "name": usecase, "desc": ""}
        )
        response = api_request(
            "POST",
            f"{api_endpoint}/libraries/{library_ref}/riskpatterns/{riskpattern_ref}/usecases",
            headers,
            usecase_data,
        )
        if response:
            cache.add("usecases", usecase_ref)
            if response == "exists":
                logging.info(f"Use Case '{usecase}' already exists. Skipping.")
            else:
                logging.info(f"Created Use Case: {usecase}")

    if threat_ref and not cache.exists("threats", threat_ref):
        threat_data = json.dumps(
            {
                "ref": threat_ref,
                "name": threat,
                "desc": threat_desc,
                "riskRating": {
                    "confidentiality": "high",
                    "integrity": "high",
                    "availability": "high",
                    "easeOfExploitation": "low",
                },
            }
        )
        response = api_request(
            "POST",
            f"{api_endpoint}/libraries/{library_ref}/riskpatterns/{riskpattern_ref}/usecases/{usecase_ref}/threats",
            headers,
            threat_data,
        )
        if response:
            cache.add("threats", threat_ref)
            if response == "exists":
                logging.info(f"Threat '{threat}' already exists. Skipping.")
            else:
                logging.info(f"Created Threat: {threat}")

    if weakness_ref and not cache.exists("weaknesses", weakness_ref):
        weakness_data = json.dumps(
            {
                "ref": weakness_ref,
                "name": weakness,
                "desc": "",
                "impact": "medium",
                "test": {"steps": "", "notes": ""},
            }
        )
        response = api_request(
            "POST",
            f"{api_endpoint}/libraries/{library_ref}/riskpatterns/{riskpattern_ref}/weaknesses",
            headers,
            weakness_data,
        )
        if response:
            cache.add("weaknesses", weakness_ref)
            if response == "exists":
                logging.info(f"Weakness '{weakness}' already exists. Skipping.")
            else:
                logging.info(f"Created Weakness: {weakness}")

    if countermeasure_ref and not cache.exists(
        "countermeasures", countermeasure_ref
    ):
        countermeasure_data = {
            "ref": countermeasure_ref,
            "name": countermeasure,
            "state": "required",
            "costRating": "medium",
        }
        if countermeasure_desc:
            countermeasure_data["desc"] = countermeasure_desc
        if (
            pd.notna(standardref)
            and standardref.lower() != "nan"
            and pd.notna(standardname)
            and standardname.lower() != "nan"
            and pd.notna(suppstandref)
            and suppstandref.lower() != "nan"
        ):
            countermeasure_data["standards"] = [
                {
                    "ref": standardref,
                    "name": standardname,
                    "supportedStandardRef": suppstandref,
                }
            ]
        response = api_request(
            "POST",
            f"{api_endpoint}/libraries/{library_ref}/riskpatterns/{riskpattern_ref}/countermeasures",
            headers,
            json.dumps(countermeasure_data),
        )
        if response:
            cache.add("countermeasures", countermeasure_ref)
            if response == "exists":
                logging.info(
                    f"Countermeasure '{countermeasure}' already exists. Skipping."
                )
            else:
                logging.info(f"Created Countermeasure: {countermeasure}")

            # Associate the countermeasure with the threat or weakness
            if threat_ref:
                if weakness_ref:
                    # Associate the countermeasure with the weakness
                    association_url = (
                        f"{api_endpoint}/libraries/{library_ref}/riskpatterns/"
                        f"{riskpattern_ref}/usecases/{usecase_ref}/threats/"
                        f"{threat_ref}/weaknesses/{weakness_ref}/countermeasures"
                    )
                else:
                    # Associate the countermeasure with the threat
                    association_url = (
                        f"{api_endpoint}/libraries/{library_ref}/riskpatterns/"
                        f"{riskpattern_ref}/usecases/{usecase_ref}/threats/"
                        f"{threat_ref}/countermeasures"
                    )
                association_data = json.dumps({"ref": countermeasure_ref})
                assoc_response = api_request(
                    "PUT", association_url, headers, association_data
                )
                if assoc_response:
                    logging.info(
                        f"Associated Countermeasure '{countermeasure}' with "
                        f"{'Weakness' if weakness_ref else 'Threat'} '{weakness if weakness_ref else threat}'."
                    )


# Log script start
logging.info("====== Starting Library Creation Process ======")

spreadsheet_location = input("What is the location of your xlsx spreadsheet? ")
final_location = spreadsheet_location.replace("\\", "/").replace('"', "")
sheet_name = input("What is the name of the spreadsheet sheet? ")

try:
    library_data = pd.read_excel(final_location, sheet_name)
except Exception as e:
    logging.error(f"Failed to read spreadsheet: {e}")
    exit(1)

build_structure_preview(library_data)
print_structure(structure_preview)

confirm = input("\nProceed with actual creation? (yes/no): ").strip().lower()
if confirm != "yes":
    logging.info("User chose not to proceed with actual creation. Exiting.")
    exit(0)

for index, row in library_data.iterrows():
    try:
        logging.info(
            f"--- Processing row {index + 1}: Library='{row['Library']}' | RiskPattern='{row['Risk_Pattern']}' | UseCase='{row['Use_Case']}'"
        )
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
    except Exception as e:
        record_summary("failed", "Row", index + 1)
        logging.error(f"❌ Failed processing row {index + 1}: {e}")

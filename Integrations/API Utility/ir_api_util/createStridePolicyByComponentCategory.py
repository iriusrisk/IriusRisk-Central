import json
import os
import sys
import requests


def read_config(config_path='config.json'):
    try:
        with open(config_path, 'r') as config_file:
            config = json.load(config_file)
            output_path = os.path.expanduser(config.get('output_path', '~/'))
            os.makedirs(output_path, exist_ok=True)
            return output_path
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error reading config file: {e}. Defaulting to home directory.")
        output_path = os.path.expanduser('~/')
        os.makedirs(output_path, exist_ok=True)
        return output_path


class IRPolicyGenerator:
    def __init__(self, token_path='~/ir/.ir_user_token', domain_path='~/ir/ir_instance_domain'):
        self.api_token, self.instance_domain = self.read_credentials(token_path, domain_path)
        self.output_path = read_config()

    def read_credentials(self, token_path, domain_path):
        try:
            with open(os.path.expanduser(token_path), 'r') as token_file:
                api_token = token_file.read().strip()
            with open(os.path.expanduser(domain_path), 'r') as domain_file:
                instance_domain = domain_file.read().strip()
            return api_token, instance_domain
        except FileNotFoundError as e:
            print(f"Error: {e}. Make sure the paths are correct.")
            sys.exit(1)

    def make_api_call(self, endpoint):
        url = f"https://{self.instance_domain}.iriusrisk.com{endpoint}"
        headers = {
            "Accept": "application/hal+json",
            "Content-Type": "application/json",
            "api-token": self.api_token
        }
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            return response.json()
        except requests.HTTPError as e:
            print(f"HTTP Error: {e}")
            print(f"Response Body: {response.text[:300]}")
            return {}
        except requests.RequestException as e:
            print(f"Error fetching API data: {e}")
            return {}

    def extract_items(self, response):
        return response.get("_embedded", {}).get("items", [])

    def prompt_choice(self, title, options, multi_select=False, name_key="name"):
        print(f"\n{title}")
        for idx, item in enumerate(options):
            print(f"{idx + 1}. {item.get(name_key)}")
        if multi_select:
            selection = input("Enter comma-separated numbers: ")
            indices = [int(i.strip()) - 1 for i in selection.split(",")]
            return [options[i] for i in indices if 0 <= i < len(options)]
        else:
            index = int(input("Select one: ")) - 1
            return options[index] if 0 <= index < len(options) else None

    def get_usecase_id(self, risk_pattern_id, stride_name):
        url = f"/api/v2/libraries/risk-patterns/{risk_pattern_id}/use-cases/summary?filter='name'='{stride_name}'"
        resp = self.make_api_call(url)
        items = self.extract_items(resp)
        return items[0]["id"] if items else None

    def get_threats(self, use_case_id):
        resp = self.make_api_call(f"/api/v2/libraries/use-cases/{use_case_id}/threats/summary")
        return self.extract_items(resp)

    def run(self):
        print("\n🛡️ Trust Zone-Based Threat Exclusion Drool Generator\n")

        # Fetch Trust Zones
        tz_data = self.make_api_call("/api/v2/trust-zones?size=2000")
        trust_zones = self.extract_items(tz_data)
        for tz in trust_zones:
            tz["displayName"] = tz["name"]
        trust_zone = self.prompt_choice("Select a Trust Zone", trust_zones, name_key="displayName")

        # Fetch Component Categories
        categories_data = self.make_api_call("/api/v2/components/categories/summary?size=2000")
        categories = self.extract_items(categories_data)

        # Fetch Libraries and filter
        libs_data = self.make_api_call("/api/v2/libraries?size=2000")
        libraries_raw = self.extract_items(libs_data)

        filtered_libs = []
        seen_names = set()

        for lib in libraries_raw:
            if "legacy" in lib["name"].lower() or "deprecated" in lib["name"].lower():
                continue
            name_clean = lib["name"].split(" - ")[0].strip().title()
            if name_clean not in seen_names:
                lib["displayName"] = name_clean
                filtered_libs.append(lib)
                seen_names.add(name_clean)

        selected_lib = self.prompt_choice("Select Component Category", filtered_libs, name_key="displayName")

        # Match to actual component category
        matched_category = next(
            (cat for cat in categories if cat["name"].lower() in selected_lib["displayName"].lower()),
            None
        )
        if not matched_category:
            print("❌ No matching component category found for this library. Exiting.")
            sys.exit(1)

        selector_line = f'isCategoryOf("{matched_category["referenceId"]}")'

        # STRIDE Use Cases
        stride_options = [
            {"id": "S", "name": "Spoofing"},
            {"id": "T", "name": "Tampering"},
            {"id": "R", "name": "Repudiation"},
            {"id": "I", "name": "Information Disclosure"},
            {"id": "D", "name": "Denial of Service"},
            {"id": "E", "name": "Elevation of Privilege"},
        ]
        stride_selected = self.prompt_choice("Select STRIDE Use Cases", stride_options, multi_select=True)
        stride_names = [s["name"] for s in stride_selected]

        reason = input("Reason for marking threats as 'Not Applicable': ").strip()
        policy_name = input("Policy name (for rule title & message): ").strip()
        filename = f"ir_policy_{policy_name.replace(' ', '_').lower()}.drl"
        filepath = os.path.join(self.output_path, filename)

        drools = f"""package com.iriusrisk.drools;

import com.iriusrisk.drools.model.*;
import com.iriusrisk.drools.model.riskpattern.*;
import com.iriusrisk.model.*;
import com.iriusrisk.drools.fact.*;
import com.iriusrisk.factories.DroolsValueConverter;
import com.iriusrisk.utils.EntityWithUDTUtil;
import com.iriusrisk.drools.fact.TagFact;

rule "{policy_name}"
no-loop
when
    $project : ProjectFact()
    $component : ComponentFact()
    TrustZoneFact($component.componentReferenceId == componentReferenceId, uuid == "{trust_zone['id']}");
    ComponentDefinitionFact({selector_line}, componentReferenceId==$component.componentReferenceId);
then
    insertLogical(new com.iriusrisk.drools.model.ComponentAlert(AlertType.INFO, "{policy_name}", "Applying {policy_name}", $component.getComponentReferenceId()));
"""

        threats_to_write = []
        risk_patterns = self.extract_items(
            self.make_api_call(f"/api/v2/libraries/{selected_lib['id']}/risk-patterns?size=2000")
        )
        for stride in stride_names:
            for rp in risk_patterns:
                uc_id = self.get_usecase_id(rp["id"], stride)
                if not uc_id:
                    continue
                threats = self.get_threats(uc_id)
                threats_to_write.extend([(t["referenceId"], stride) for t in threats])

        for threat_id, stride in threats_to_write:
            drools += f"    insertLogical(new ChangeComponentThreatStateFact($component.getComponentReferenceId(), \"{threat_id}\", \"Not Applicable\", \"{reason}\"));\n"

        drools += "end\n"

        with open(filepath, "w") as f:
            f.write(drools)

        print(f"\n✅ Drools file written to: {filepath}")


if __name__ == "__main__":
    IRPolicyGenerator().run()

import json
import os
import sys
import subprocess


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


def prompt_choice(title, options, multi_select=False, name_key="name"):
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


def run_script(script_name, arg=None):
    cmd = ["python3", script_name]
    if arg:
        cmd.append(arg)
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"❌ Error running {script_name}:\n{result.stderr}")
        sys.exit(1)
    return result.stdout


def load_tmp(filename):
    with open(filename, "r") as f:
        return json.load(f)


def main():
    output_path = read_config()

    # 1. Select Trust Zone
    run_script("fetch_trust_zones.py")
    tz_list = load_tmp(os.path.join(output_path, "trust_zones.tmp"))
    trust_zone = prompt_choice("Select Trust Zone", tz_list)
    if not trust_zone:
        sys.exit("❌ No Trust Zone selected.")

    # 2. Select Component Category
    run_script("fetch_components_categories.py")
    categories = load_tmp(os.path.join(output_path, "component_categories.tmp"))
    selected_cat = prompt_choice("Select Component Category", categories)
    if not selected_cat:
        sys.exit("❌ No Component Category selected.")

    # 3. Select STRIDE Categories
    stride_options = [
        {"id": "S", "name": "Spoofing"},
        {"id": "T", "name": "Tampering"},
        {"id": "R", "name": "Repudiation"},
        {"id": "I", "name": "Information Disclosure"},
        {"id": "D", "name": "Denial of Service"},
        {"id": "E", "name": "Elevation of Privilege"},
    ]
    selected_stride = prompt_choice("Select STRIDE Categories", stride_options, multi_select=True)
    stride_names = set(s['name'] for s in selected_stride)

    # 4. Prompt for Reason & Policy Name
    reason = input("Reason for marking threats as 'Not Applicable': ").strip()
    policy_name = input("Policy name (for rule title & message): ").strip()
    filename = f"ir_policy_{policy_name.replace(' ', '_').replace('-', '_').lower()}.drl"
    filepath = os.path.join(output_path, filename)

    # 5. Fetch Components for the selected category
    run_script("fetch_components.py", selected_cat["name"])
    components = load_tmp(os.path.join(output_path, "components.tmp"))

    threat_ids = set()

    for comp in components:
        print(f"🔍 Component: {comp['name']}")
        run_script("fetch_component_risk_patterns.py", comp['id'])
        risk_patterns = load_tmp(os.path.join(output_path, "component_risk_patterns.tmp"))

        for rp in risk_patterns:
            run_script("fetch_risk_pattern_use_cases.py", rp['id'])
            use_cases = load_tmp(os.path.join(output_path, "risk_pattern_use_cases.tmp"))

            for uc in use_cases:
                if uc['name'] not in stride_names:
                    continue
                print(f"   ↳ STRIDE Use Case: {uc['name']}")
                run_script("fetch_use_case_threats.py", uc['id'])
                threats = load_tmp(os.path.join(output_path, "use_case_threats.tmp"))
                for threat in threats:
                    if "referenceId" in threat:
                        threat_ids.add(threat["referenceId"])

    # Generate Drools rule
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
    ComponentDefinitionFact(isCategoryOf("{selected_cat['referenceId']}"), componentReferenceId == $component.componentReferenceId);
then
    insertLogical(new ComponentAlert(AlertType.INFO, "{policy_name}", "{reason}", $component.getComponentReferenceId()));
"""

    for threat_id in sorted(threat_ids):
        drools += f'    insertLogical(new ChangeComponentThreatStateFact($component.getComponentReferenceId(), "{threat_id}", "Not Applicable", "{reason}"));\n'

    drools += "end\n"

    with open(filepath, "w") as f:
        f.write(drools)

    print(f"\n✅ Drools file written to: {filepath}")


if __name__ == "__main__":
    main()

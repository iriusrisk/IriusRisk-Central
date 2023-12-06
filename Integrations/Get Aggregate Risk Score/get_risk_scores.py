import requests
import json
import argparse



def get_risk_score(project_name, sub_domain, api_key):
    responses = []

    # Get risks for the project
    url_project_risks = f"https://{sub_domain}.iriusrisk.com//api/v1/products/{project_name}/risks"
    #print(url_project_risks)

    payload = {}
    headers = {
        'Accept': 'application/json',
        'api-token': f'{api_key}'
    }

    response_project_risks = requests.get(url_project_risks, headers=headers, data=payload)
    responses.append(response_project_risks.text)
    print(project_name, response_project_risks.text)

    # Get components from the project
    url_project_details = f"https://{sub_domain}.iriusrisk.com//api/v1/products/{project_name}"

    payload = {}
    headers = {
        'Accept': 'application/json',
        'api-token': f'{api_key}'
    }

    response_project_details = requests.get(url_project_details, headers=headers, data=payload)

    if response_project_details.status_code == 200:
        json_data = response_project_details.json()

    first_layer = json_data.get("name")
    if first_layer:
        components_list = json_data.get("components")
        if components_list:
            for component in components_list:
                third_layer_name = component.get("name")
                if third_layer_name:
                    # Calls the components and checks for project that exist based on naming convention
                    project_component_name = third_layer_name.replace("-", "")
                    project_component_name = project_component_name.replace(" ", "-").lower()
                    project_component_name = project_component_name.replace("--", "-")

                    url_component_risks = f"https://{sub_domain}.iriusrisk.com//api/v1/products/{project_component_name}/risks"

                    payload = {}
                    headers = {
                        'Accept': 'application/json',
                        'api-token': f'{api_key}'
                    }

                    response_component_risks = requests.get(url_component_risks, headers=headers, data=payload)

                    if response_component_risks.status_code == 200:
                        responses.append(response_component_risks.text)
                        print(project_component_name, response_component_risks.text)

            # Initialize variables
            total_residual_risk = 0
            num_responses = len(responses)

            # Parse JSON responses and calculate total residual risk
            for response in responses:
                data = json.loads(response)
                residual_risk = data.get("residualRisk", 0)
                total_residual_risk += residual_risk

            # Calculate average residual risk
            average_residual_risk = round(total_residual_risk / num_responses, 2)

            # Print the result
            print(f"Average Residual Risk: {average_residual_risk}")

    url = f"https://{sub_domain}.iriusrisk.com//api/v1/products/{project_name}"

    payload = json.dumps({
        "name": f"{project_name}",
        "desc": "",
        "tags": "",
        "udts": [
            {
                "ref": "overall_risk",
                "value": f"{average_residual_risk}"
            }
        ]
    })
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'api-token': f'{api_key}'
    }

    response = requests.request("PUT", url, headers=headers, data=payload)

    print(response.text)
    if response.status_code == 200:
        print("Custom Field was Updated")


def main():
    parser = argparse.ArgumentParser(description="Retrieve and calculate average residual risk for a project")
    parser.add_argument("project_name", help="Name of the project")
    parser.add_argument("sub_domain", help="Subdomain of the IriusRisk instance")
    parser.add_argument("api_key", help="API key for authentication")

    args = parser.parse_args()

    # Call your function with command line arguments
    get_risk_score(args.project_name, args.sub_domain, args.api_key)

if __name__ == "__main__":
    main()


import requests
import json
import config
import pandas as pd

#config is used to import the API key into the below API calls

url = f"https://{config.sub_domain}.iriusrisk.com/api/v2/components?size=100000"

headers = {
    'Accept': 'application/hal+json',
    'api-token': config.api_key
}

response = requests.get(url, headers=headers)

if response.status_code == 200:
    json_data = response.json()

    embedded_data = json_data.get("_embedded")

    if embedded_data:
        items = embedded_data.get("items")

        if items:
            for item in items:
                name = item.get("name")
                component_id = item.get('id')
                visible = item.get("visible")
                description = item.get("description")

                category = item.get('category')
                category_name = category.get('name')
                category_id = category.get('id')

                #leverage the following section if you want to hide or make non-visible certain categories of applications
                #if category_name == 'Data store' or category_name == 'Server-side':
                    #visible = 'false'

                    #populate this list to the if category_name above -
                    # category_name == 'Data-store'
                    # category_name == 'Server-side'
                    # category_name == 'Client-side'
                    # category_name == 'Environment'
                    # category_name == 'Microsoft Azure'
                    # category_name == 'Regulatory'
                    # category_name == 'General'
                    # category_name == 'Message Broker'
                    # category_name == 'On Premise Architecture'
                    # category_name == 'Docker'
                    # category_name == 'Google Cloud Platform'
                    # category_name == 'Amazon Web Services'
                    # category_name == 'Functional'
                    # category_name == 'Regulatory'
                    # category_name == 'IoT components'
                    # category_name == 'Kubernetes'
                    # category_name == 'Microservices architecture'
                    # category_name =='Automotive'
                    # category_name == 'Custom'
                    # category_name == 'IEC62243'
                    # category_name == 'Financial'
                    # category_name == 'Policy Group'
                    # category_name == 'VPC Types'
                    # category_name == 'Project Components'
                    # category_name == 'Hardware'
                    # category_name == 'Boundary Devices'
                    # category_name == 'Virtual Components'
                    # category_name == 'VMWare'
                    # category_name == 'Generic Components'
                    # category_name == 'Network Components'
                    # category_name == 'Oracle Cloud Infrastructure'
                    # category_name == 'SAP Components'
                    # category_name == 'ML/AI'
                    # category_name == 'Message Broker'
                    # category_name == 'Salesforce components'

                url = f"https://{config.sub_domain}.iriusrisk.com/api/v2/components/{component_id}"

                payload = json.dumps({
                    "category": {
                        "id": category_id,
                        "name": category_name
                    },
                    "name": name,
                    "referenceId": component_id,
                    "visible": visible,
                    "description": description
                })

                headers = {
                    'Content-Type': 'application/json',
                    'Accept': 'application/hal+json',
                    'api-token': config.api_key
                }

                response = requests.put(url, headers=headers, data=payload)

                if response.status_code == 200:
                    print(f"{response.status_code} - Component {name} - UPDATE SUCCESSFUL")
                    #print(response.text)
                else:
                    print(response.text)

        print('\n')
        print(len(items), "found and updated")

    else:
        print("No embedded data found in the response.")
else:
    print(f"Request failed with status code: {response.status_code}")
    print(response.text)

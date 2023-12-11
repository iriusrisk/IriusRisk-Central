import requests
import json
import config


def assoc_standard_to_cms(countermeasure, standard_ref, reference):

  baseurl = config.baseUrl
  api_token = config.API_KEY
  countermeasure_id = countermeasure.replace(" ", "-")
  api_endpoint = f"{baseurl}/api/v1/security-content/countermeasures/{countermeasure_id}/standards"

  payload = json.dumps([
    {
      "standardRef": f"{standard_ref}",
      "reference": f"{reference}"
    }
    ])

  headers = {
    "API-token": api_token,
    "Content-Type": "application/json",
    "Accept": "application/json"
  }

  response = requests.post(api_endpoint, data=payload, headers=headers)
  print(response.text)
  print(response)


def loop_standards_to_cms():
  with open('standards_to_cms.txt', 'r') as file:
    for line in file:
      # Split the line into individual parameters
      countermeasure, standard_ref, reference = line.strip().split(',')

      # Call the assoc_standard_to_cms function with the extracted parameters
      assoc_standard_to_cms(countermeasure, standard_ref, reference)


loop_standards_to_cms()

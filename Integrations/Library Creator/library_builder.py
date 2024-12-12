import requests
import json
import time
import pandas as pd
import config

def library_creation(library, riskpattern, usecase, threat, threat_desc, weakness, countermeasure, countermeasure_desc, standardref, standardname,suppstandref):

  api_endpoint = config.URL
  #adds the API token from a seperate file
  api_token = config.API_KEY

  #CREATES THE LIBRARY

  library_endpoint = api_endpoint + "/libraries"

  library_ref = library.replace(" ","-")

  library_data = json.dumps({
    "ref" : f"{library_ref}",
    "name" : f"{library}",
    "desc" : ""
  })

  headers = {
    "Content-Type": "application/json",
    "Accept": "application/json",
    "API-token": f"{api_token}"
  }

  response = requests.post(library_endpoint, headers=headers, data=library_data)
  if response.status_code == 201:
    print(response, "Library was created")
  elif response.status_code == 400:
    response = requests.put(library_endpoint, headers=headers, data=library_data)
    if response.status_code == 201:
      print(response, "Library was updated")
    elif response.status_code == 405:
      print(response, "METHOD NOT ALLOWED - Library not updated!")

  #time.sleep(2)

  #CREATES THE RISK PATTERN

  riskpattern_endpoint = api_endpoint + f"/libraries/{library_ref}/riskpatterns"

  #print(riskpattern_endpoint)

  riskpattern_ref = riskpattern.replace(" ", "")

  payload = json.dumps({
    "ref": f"{riskpattern_ref}",
    "name": f"{riskpattern}",
    "desc": "",
    #"tags": [
      #"string",
      #"string"
    #]
  })
  headers = {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
    'API-token': api_token
  }

  response = requests.request("POST", riskpattern_endpoint, headers=headers, data=payload)
  print(response, "Risk Pattern")
  #print(response.text)


  #CREATES THE USE CASE

  usecase_endpoint = api_endpoint + f"/libraries/{library_ref}/riskpatterns/{riskpattern_ref}/usecases"

  usecase_ref = usecase.replace(" ", "-")

  usecase_data = json.dumps({
    "ref": f"{usecase_ref}",
    "name": f"{usecase}",
    "desc": ""
  })

  response = requests.post(usecase_endpoint, headers=headers, data=usecase_data)
  print(response, "Use Case")

  #time.sleep(2)

  #CREATES THE THREATS

  threat_endpoint = api_endpoint + f"/libraries/{library_ref}/riskpatterns/{riskpattern_ref}/usecases/{usecase_ref}/threats"

  #print(threat_endpoint)

  threat_ref = threat.replace(" ", "-")

  #the only values accepted for riskRating are "[The only risk rating acceptable values are: none, low, medium, high, very-high]"
  threat_data = json.dumps({
    "ref": f"{threat_ref}",
    "name": f"{threat}",
    "desc": f"{threat_desc}",
    "riskRating": {
      "confidentiality": "high",
      "integrity": "high",
      "availability": "high",
      "easeOfExploitation": "low"
      }
    })

  response = requests.post(threat_endpoint, headers=headers, data=threat_data)
  print(response, "Threat")
  #print(response.text, "Threat Response")

  #CREATES A WEAKNESS IN A RISK PATTERN

  weakness_ref = weakness.replace(" ","-")

  weakness_creation_endpoint = api_endpoint + f"/libraries/{library_ref}/riskpatterns/{riskpattern_ref}/weaknesses"

  weakness_data = json.dumps({
  "ref": f"{weakness_ref}",
  "name": f"{weakness}",
  "desc": "",
  "impact": "medium",
  "test": {
    "steps": "",
    "notes": ""
  }
  })

  response = requests.post(weakness_creation_endpoint, headers=headers, data=weakness_data)
  print(response, "Weakness")
  #print(response.text)

  #ASSOCIATES A WEAKNESS TO A THREAT

  associate_weakness_endpoint = api_endpoint + f"/libraries/{library_ref}/riskpatterns/{riskpattern_ref}/usecases/{usecase_ref}/threats/{threat_ref}/weaknesses"

  data = json.dumps({
  "ref": f"{weakness_ref}"
  })

  response = requests.put(associate_weakness_endpoint, headers=headers, data=data)
  print(response, "Weakness Associated")
  #print(response.text)

  #CREATES A NEW COUNTERMEASURE IN A RISK PATTERN
    #for some reason, it is not taking the mitigation value.

  countermeasure_creation_endpoint = api_endpoint + f"/libraries/{library_ref}/riskpatterns/{riskpattern_ref}/countermeasures"

  countermeasure_ref = countermeasure.replace(" ","_")

  countermeasure_data = json.dumps({
  "ref": f"{countermeasure_ref}",
  "name": f"{countermeasure}",
  "desc": countermeasure_desc,
  #"mitigation": "",
  "test": {
    "steps": "",
    "notes": ""
  },
  "state": "required",
  "costRating": "medium",
  "standards": [
    {
      "ref": f"{standardref}",
      "name": f"{standardname}",
      "supportedStandardRef": f"{suppstandref}"
    },
  ]
  })

  response = requests.post(countermeasure_creation_endpoint,headers=headers, data=countermeasure_data)
  print(response, "Countermeasure")
  #print(response.text)

  #ASSOCIATES A CM WITH A WEAKNESS

  associate_cm_endpoint = api_endpoint + f"/libraries/{library_ref}/riskpatterns/{riskpattern_ref}/usecases/{usecase_ref}/threats/{threat_ref}/weaknesses/{weakness_ref}/countermeasures"

  data = json.dumps({
  "ref": f"{countermeasure_ref}"
  })

  response = requests.put(associate_cm_endpoint, headers=headers, data=data)
  print(response, "CM Associated")
  #print(response.text)

  print(f"Row {counter} Complete")
  print("")

import pandas as pd

spreadsheet_location = input("What is the location of your xlsx spreadsheet? ")

final_location = spreadsheet_location.replace("\\", "/").replace('"','')

sheet_name = input("What is the name of the spreadsheet sheet? ")

library_data = pd.read_excel(final_location, sheet_name)


counter = 1

for index, row in library_data.iterrows():

  counter += 1

  #create a spreadsheet with column headers and match those the variables in this script.


  library = str(row['Library'])
  riskpattern = str(row['Risk_Pattern'])
  #riskpattern_id = str(row['Risk_Pattern_ID'])
  usecase = str(row['Use_Case'])
  #usecase_id = str(row['Use_Case_ID'])
  threat = str(row['Threat'])
  #threat_id = str(row['Threat_ID'])
  threat_desc = str(row['Threat_Desc'])
  weakness = str(row['Weakness'])
  #weakness_id = str(row['Weakness_ID'])
  countermeasure = str(row['CM'])
  #countermeasure_id = str(row['CM_ID'])
  countermeasure_desc = str(row['CM_Desc'])
  standardref = str(row['standardref'])
  standardname = str(row['standardname'])
  suppstandref = str(row['supported standardref'])

  library_creation(library, riskpattern, usecase, threat, threat_desc, weakness, countermeasure, countermeasure_desc, standardref, standardname,suppstandref)

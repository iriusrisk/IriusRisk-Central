import pip._vendor.requests as requests
import sys
import json

#-------------INITIALISE ENVIRONMENT-----------------#
#set request and head
start_domain = 'https://<domain-1>.iriusrisk.com'
start_sub_url = '' #initialise
start_apitoken = '<insert_api_token>' #insert api token value
start_head = {'api-token': start_apitoken}

post_domain = 'https://<domain-2>.iriusrisk.com'
post_sub_url = ''
post_apitoken = '<insert_api_token>'
post_head = {'api-token': post_apitoken}


#-------------GET ALL ROLES-----------------------#
#update url
start_sub_url = '/api/v2/business-units'
start_url = start_domain + start_sub_url

#GET request
response = requests.get(start_url, headers=start_head)

#If successful
if response.status_code == 200:
  print("Get request successful")
  data = response.json()
  #print(data)
  
  filtered_data = [item for item in data['_embedded']["items"]]

#if unauthorised
elif response.status_code == 401:
  print("User is unauthorised1. Please check your api token is valid, that your api is enabled in the settings & that you have appropriate permissions on your account")
  sys.exit() #if unauthorised, exit the script

#catch
else:
  print("Request: " + response.request.method + ' ' + start_url + " failed")
 
#------------POST ALL ROLES-----------------------#

#FILTER results to get the name and description
post_sub_url = '/api/v2/business-units'
post_url = post_domain + post_sub_url  
for item in filtered_data:
  myobj = {f"referenceId": item['referenceId'],
        "name": item['name'],
        "description":item['description']}
  
  post_head={'api-token': post_apitoken}

  #post new roles
  response = requests.post(post_url, headers=post_head, json = myobj)
  
  if response.status_code==200:
    print("successful post")
    data_new_role = response.json()
    filtered_new_role_data = [item for item in data['id']]
    
  #if unauthorised
  elif response.status_code == 401:
    print("User is unauthorised. Please check your api token is valid, that your api is enabled in the settings & that you have appropriate permissions on your account")
    sys.exit() #if unauthorised, exit the script
    
  else:
    print("Request: " + response.request.method + ' ' + item['name'] + ' ' + post_url + " failed. This BU likely exists already\n")

  


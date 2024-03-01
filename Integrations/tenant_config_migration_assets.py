import pip._vendor.requests as requests
import sys
import json


#-------------INITIALISE ENVIRONMENT-----------------#
#set request and head
start_domain = 'https://markd.iriusrisk.com'
start_sub_url = '' #initialise
start_apitoken = '909c43c0-8dfb-47c1-b0f1-0b852b42178d' #insert api token value
start_head = {'api-token': start_apitoken}

post_domain = 'https://tt-20.iriusrisk.com'
post_sub_url = ''
post_apitoken = 'f2e3f28b-3b0f-4893-9bbf-31ce68bdedfb'
post_head = {'api-token': post_apitoken}

#-------------GET ALL ASSETS domain 1-----------------------#
#update url
start_sub_url = '/api/v2/assets'
start_url = start_domain + start_sub_url

#GET request
response = requests.get(start_url, headers=start_head)

print("\n DOMAIN 1 \n")
#If successful
if response.status_code == 200:
    print("Get request successful")
    data1 = response.json()

#-------------GET ALL ASSETS domain 2-----------------------#
#update url
post_sub_url = '/api/v2/assets'
post_url = post_domain + post_sub_url

#GET request
response = requests.get(post_url, headers=post_head)

print("\n DOMAIN 2 \n")
#If successful
if response.status_code == 200:
    print("Get request successful")
    data2 = response.json()

#initialise dictionairies
myobj = {}
ids_mapping = {}

#-------------- GET ALL SECURITY CLASSIFICATIONS domain 1-----------------#
#these items get passed in as the security classification id inside the post request for assets
#update url
start_sub_url = '/api/v2/security-classifications'
start_url = start_domain + start_sub_url

#GET request
response = requests.get(start_url, headers=start_head)

print("\n DOMAIN 1 - Security-classifications\n")
#If successful
if response.status_code == 200:
    print("Get request successful")
    data3 = response.json()


#---------------GET ALL SECURITY CLASSIFICATIONS domain 2 ----------------#
post_sub_url = '/api/v2/security-classifications'
post_url = post_domain + post_sub_url

#GET request
response = requests.get(post_url, headers=post_head)
data4 = response.json()


print("\n DOMAIN 2 - Security-classifications\n")
#If successful
if response.status_code == 200:
    print("Get request successful")
    data4 = response.json()

#------------ ITERATE OVER THE DATA FROM BOTH APIS
for item3 in data3['_embedded']['items']:
    for item4 in data4['_embedded']['items']:
        # Check if the name matches
        if item3['name'] == item4['name']:
            # Extract the IDs            
            id_from_api3 = item3['id'],
            name_from_api_3 = item3['name'],
            id_from_api4 = item4['id'],
            name_from_api_4 = item4['name']
            
            #save the results to a new dict so we can call this later
            ids_mapping[item3['name']] = {'id_from_api3': id_from_api3, 'id_from_api4': id_from_api4}


#print in a formatted, nice list.
print('\nSecurity Classifications available and their associated ids:\n')
for name, ids in ids_mapping.items():
    print(name, ids) #print the set of key and values. Names and ids
    print() # Empty line after each category         


#------------POST ALL ASSETS -----------------------#


post_sub_url = '/api/v2/assets'
post_url = post_domain + post_sub_url

for item1 in data1["_embedded"]['items']:
    #get the security classification id's to pass
    #align the id for the 2nd environment where the name matches what we have in the first
    for name, ids in ids_mapping.items():
        if name==item1['securityClassification']['name']:
            ref_id = ids['id_from_api4']
            ref_id_filtered = ref_id[0]           
    
    #get the object to pass in the post data                
    myobj = {
        "name": item1['name'],
        "description": item1['description'],
        "securityClassification": {
           "id": ref_id_filtered
        }
    }

    post_head={'api-token': post_apitoken}
    #post new roles
    response = requests.post(post_url, headers=post_head, json = myobj)
    
    if response.status_code==200:
        print("successful post of asset: " + item1['name'])
        data_new_asset = response.json()
        
    #if unauthorised
    elif response.status_code == 401:
        print("User is unauthorised. Please check your api token is valid, that your api is enabled in the settings & that you have appropriate permissions on your account")
        sys.exit() #if unauthorised, exit the script
        
    else:
        #print(response.json())
        print("Request: " + response.request.method + ' ' + item1['name'] + ' ' + post_url + " failed. This asset likely exists already\n")

    

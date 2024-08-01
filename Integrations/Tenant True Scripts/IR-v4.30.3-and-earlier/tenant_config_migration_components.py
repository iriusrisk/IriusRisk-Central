import pip._vendor.requests as requests
import sys
import json
import config


#-------------INITIALISE ENVIRONMENT-----------------#
#set request and head
start_domain = config.start_domain
start_sub_url = '' #initialise
start_apitoken = config.start_apitoken #insert api token value
start_head = {'api-token': start_apitoken}

post_domain = config.post_domain
post_sub_url = ''
post_apitoken = config.post_apitoken
post_head = {'api-token': post_apitoken}


element_size = '?size=10000'
sys.stdout.reconfigure(encoding='utf-8')


#-------------GET ALL COMPONENTS domain 1-----------------------#
#update url
start_sub_url = '/api/v2/components' + element_size
start_url = start_domain + start_sub_url

#GET request
response = requests.get(start_url, headers=start_head)

print("\n DOMAIN 1 \n")
#If successful
if response.status_code == 200:
    print("Get request successful")
    data1 = response.json()
    #print(data1)

#-------------GET ALL COMPONENTS domain 2-----------------------#
#update url
post_sub_url = '/api/v2/components' + element_size
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
ids_names_mapping = {}

#-------------- GET ALL COMPONENT CATEGORIES domain 1-----------------#
#these items get passed in as the component categori id, name inside the post request for assets
#update url
start_sub_url = '/api/v2/components/categories' + element_size
start_url = start_domain + start_sub_url

#GET request
response = requests.get(start_url, headers=start_head)

print("\n DOMAIN 1 - Categories\n")
#If successful
if response.status_code == 200:
    print("Get request successful")
    data3 = response.json()


#---------------GET ALL COMPONENT CATEGORIES domain 2 ----------------#
post_sub_url = '/api/v2/components/categories' + element_size
post_url = post_domain + post_sub_url

#GET request
response = requests.get(post_url, headers=post_head)
data4 = response.json()


print("\n DOMAIN 2 - Component Categories\n")
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
            ids_names_mapping[item3['name']] = {'id_from_api3': id_from_api3, 'id_from_api4': id_from_api4}
            
            
#------------POST ALL ASSETS -----------------------#


post_sub_url = '/api/v2/components/categories'
post_url = post_domain + post_sub_url

print('\nStarting post process - component categories')

for item3 in data3["_embedded"]['items']:
    #get the category id's to pass
    #align the id for the 2nd environment where the name matches what we have in the first
    
    #get the object to pass in the post data                
    myobj = {
        "referenceId": item3['referenceId'],
        "name": item3['name']
    }

    post_head={'api-token': post_apitoken}
    #post new roles
    response = requests.post(post_url, headers=post_head, json = myobj)
    
    if response.status_code==200:
        print("successful post of component category: " + item3['name'])
        data_new_component = response.json()
        
    #if unauthorised
    elif response.status_code == 401:
        print("User is unauthorised. Please check your api token is valid, that your api is enabled in the settings & that you have appropriate permissions on your account")
        sys.exit() #if unauthorised, exit the script

    #commented out to reduce noise. Any issues, remove the comments.
    #else:
        #print(response.json())
        #print("Request: " + response.request.method + ' ' + item3['name'] + ' ' + post_url + " failed. This component category likely exists already\n")

print('Finished post process - component categories')

#------------POST ALL ASSETS -----------------------#


post_sub_url = '/api/v2/components'
post_url = post_domain + post_sub_url

print('\nStarting post process - components')

for item1 in data1["_embedded"]['items']:
    #get the category id's to pass
    #align the id for the 2nd environment where the name matches what we have in the first
    for name, ids in ids_names_mapping.items():
        if name==item1['category']['name']:
            ref_id = ids['id_from_api4']
            ref_name = name
            ref_id_filtered = ref_id[0]           
    
    #get the object to pass in the post data                
    myobj = {
        "referenceId": item1['referenceId'],
        "name": item1['name'],
        "description": item1['description'],
        "category": {
           "id": ref_id_filtered,
           "name": ref_name
        },
        "visible": item1['visible']
    }

    post_head={'api-token': post_apitoken}
    #post new roles
    response = requests.post(post_url, headers=post_head, json = myobj)
    
    if response.status_code==200:
        print("successful post of component: " + item1['name'])
        data_new_component = response.json()
        
    #if unauthorised
    elif response.status_code == 401:
        print("User is unauthorised. Please check your api token is valid, that your api is enabled in the settings & that you have appropriate permissions on your account")
        sys.exit() #if unauthorised, exit the script
    
    #I have commented this else statement out in the interest of managing noise. 
    #A default environment will have > 850 components.
    #You can use this for testing, but please note that there will be at least 850 entries.
        
    #else:
        #print(response.json())
        #print("Request: " + response.request.method + ' ' + item1['name'] + ' ' + post_url + " failed. This component likely exists already\n")

print('Finished post process - components')

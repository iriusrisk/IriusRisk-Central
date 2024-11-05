import pip._vendor.requests as requests
import sys
import config

# ------------- INITIALIZE ENVIRONMENT ----------------- #
#set request and head
start_domain = config.start_domain
start_sub_url = config.start_sub_url
start_apitoken = config.start_apitoken
start_head = config.start_head

post_domain = config.post_domain
post_sub_url = config.post_sub_url
post_apitoken = config.post_apitoken
post_head = config.post_head

sub_url = "/api/v2/security-classifications"

# ------------- FUNCTIONS ----------------------- #

def handle_unsuccessful_response(response, url):
    if response.status_code == 401:
        print(
            "User is unauthorized. Please check if your API token is valid, API is enabled in settings, and you have appropriate permissions."
        )
    else:
        print(
            f"Request {response.request.method} {url} failed with status code {response.status_code}"
        )
    sys.exit()

# Returns a list of roles from 
def fetch_roles(url, headers):
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        print("GET request successful")
        data = response.json()
        items = data["_embedded"]["items"]

        roles =[]

        for role in items:
          role_data = {
              "id": role["id"],
              "referenceId": role["referenceId"],
              "name": role["name"],
              "description": role["description"],
              "confidentiality": role["confidentiality"],
              "integrity": role["integrity"],
              "availability": role["availability"],
          }
          roles.append(role_data)
        
        return roles
    else:
        handle_unsuccessful_response(response, url)

# Finds matches in reference ids between source and destination
def find_matches(list_1, list_2):
    combined = list_1 + list_2

    referenceIds = []
    for i in range(0, len(combined)):
        referenceIds.append(combined[i]["referenceId"])

    matches = {x for x in referenceIds if referenceIds.count(x) > 1}

    matches_dict = {}

    for role in list_2:
        if role["referenceId"] in matches:
            matches_dict[role["referenceId"]] = role["id"]
    
    return matches_dict

# Sends a PUT request to update
def put_role(uuid, role, url, headers):
    
    # These wont be accepted by PUT endpoint
    del role['referenceId']
    
    response = requests.put(url+"/"+uuid, headers=headers, json=role)

    if response.status_code == 200:
         print("PUT request successful")
    else :
        handle_unsuccessful_response(response, url)

# Sends a POST request to create new 
def post_role(role, url, headers):
    
    # POST request wont accept this
    del role['id']
    response = requests.post(url, headers=headers, json=role)
    if response.status_code == 200:
        print("POST request successful")
    else:
        handle_unsuccessful_response(response, url)

# Checks if PUT request has the same details to save calling the API
def is_role_same(role, destination_roles):
    referenceId = role["referenceId"]
    for dest_role in destination_roles:
        if referenceId == dest_role["referenceId"] :
          del role['id']
          del dest_role['id']
          if role == dest_role:
              return True
          else :
              return False
    return False

    
# ------------- MAIN EXECUTION ----------------------- #
# N.B. Reference Id's must be the same at source and destination for PUT to update,
# otherwise POST will be called and new entry created

# Logic flow as follows:
#   1. Get roles from origin
#   2. Get roles from destination
#   3. Find duplicate referenceId's
#   4. For each duplicate referenceId, find the associated uuid in the destination and place it in a dict
#   5. loop through all roles from source
#     a. If referenceId exists in matches then find UUID and perform put
#     b. Else perform POST

if __name__ == "__main__":
    start_roles = fetch_roles(start_domain + sub_url, start_head)
    put_roles = fetch_roles(post_domain + sub_url, post_head)

    matches = find_matches(start_roles, put_roles)

    for role in start_roles:
        if role["referenceId"] in matches:
            if is_role_same(role, put_roles) is False:
              uuid = matches[role["referenceId"]]
              put_role(uuid, role, post_domain + sub_url, post_head)
        else :
            post_role(role, post_domain + sub_url, post_head)

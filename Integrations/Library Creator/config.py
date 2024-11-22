#-------------INITIALISE ENVIRONMENT-----------------#
#set request and head
source_domain = 'https://ps-001.iriusrisk.com' # source domain
source_sub_url = '/api/v2/roles' #initialise
source_apitoken = 'd1fdc8f5-b6cf-4c3c-8699-fb249f057c43' #insert api token value
source_head = {'api-token': source_apitoken, "size":"40"}

dest_domain = 'https://ps-002.iriusrisk.com' # target domain
dest_sub_url = '/api/v2/roles'
dest_apitoken = 'fd761a24-3bb1-4e0f-a741-b58d7eb70e80'
dest_head = {'api-token': dest_apitoken, 'size':"40"}
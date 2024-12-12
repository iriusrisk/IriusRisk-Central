#-------------INITIALISE ENVIRONMENT-----------------#
#set request and head
source_domain = '' # source domain
source_sub_url = '/api/v2/roles' #initialise
source_apitoken = '' #insert api token value
source_head = {'api-token': source_apitoken, "size":"40"}

dest_domain = '' # target domain
dest_sub_url = '/api/v2/roles'
dest_apitoken = ''
dest_head = {'api-token': dest_apitoken, 'size':"40"}

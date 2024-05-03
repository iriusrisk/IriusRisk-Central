import pip._vendor.requests as requests
import sys
import json

#-------------INITIALISE ENVIRONMENT-----------------#
#set request and head
start_domain = 'https://<insert_domain_name>.iriusrisk.com' # source domain
start_sub_url = '' #initialise
start_apitoken = '<insert_adpi_token>' #insert api token value
start_head = {'api-token': start_apitoken}

post_domain = 'https://<insert_domain_name>.iriusrisk.com' # target domain
post_sub_url = ''
post_apitoken = '<insert_adpi_token>'
post_head = {'api-token': post_apitoken}
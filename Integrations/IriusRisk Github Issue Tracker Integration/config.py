#----IriusRisk----
domain = 'https://<insert_IriusRisk_domain>.iriusrisk.com'
sub_url = '/api/v1/products' #initialise
sub_url_api_v2 = '/api/v2/projects'
apitoken = '<insert_IriusRisk_api_token>' #IriusRisk API token
head = {'api-token': apitoken}

#----Github----
owner = "<insert_github_organization>" #GH org
repo = "<insert_github_repo>" #GH project
personal_access_token = "<insert_Github_personal_access_token>" #GH Personal access token
GH_head = {'Authorization': 'Bearer ' + personal_access_token}
# Purpose 

 The purpose of this API script ot hide or make visibiliy large quantities of IriusRisk components through the API based upon the category they are in. 
 
# Requirements 
1. Create a config.py file to store your API key and sub-domain information in the same directory as this file. It should contain the following variables: 

  ```Python
    api_key = '{your_api_key}'
    sub_domain = '{your_sub_domain}'
  ```

# Usage
1. Run the script and substitute which sets of categories need to be hidden by substituting them in the following code block and uncommenting this block of code. Without this code block, it is essentially getting all of the components and then re-putting them back into IriusRisk with no changes. The following component categories are accurate as of v4.23 (December 2023): 

``` Python
    #leverage the following section if you want to hide or make non-visible certain categories of applications
                #if category_name == 'Data store' or category_name == 'Server-side':
                    #visible = 'false'

                    #populate this list to the if category_name above -
                    # category_name == 'Data-store'
                    # category_name == 'Server-side'
                    # category_name == 'Client-side'
                    # category_name == 'Environment'
                    # category_name == 'Microsoft Azure'
                    # category_name == 'Regulatory'
                    # category_name == 'General'
                    # category_name == 'Message Broker'
                    # category_name == 'On Premise Architecture'
                    # category_name == 'Docker'
                    # category_name == 'Google Cloud Platform'
                    # category_name == 'Amazon Web Services'
                    # category_name == 'Functional'
                    # category_name == 'Regulatory'
                    # category_name == 'IoT components'
                    # category_name == 'Kubernetes'
                    # category_name == 'Microservices architecture'
                    # category_name =='Automotive'
                    # category_name == 'Custom'
                    # category_name == 'IEC62243'
                    # category_name == 'Financial'
                    # category_name == 'Policy Group'
                    # category_name == 'VPC Types'
                    # category_name == 'Project Components'
                    # category_name == 'Hardware'
                    # category_name == 'Boundary Devices'
                    # category_name == 'Virtual Components'
                    # category_name == 'VMWare'
                    # category_name == 'Generic Components'
                    # category_name == 'Network Components'
                    # category_name == 'Oracle Cloud Infrastructure'
                    # category_name == 'SAP Components'
                    # category_name == 'ML/AI'
                    # category_name == 'Message Broker'
                    # category_name == 'Salesforce components'
```
# Results

The following output should be seen for all components - 

```Python
    "{response.status_code} - Component {name} - UPDATE SUCCESSFUL"
```

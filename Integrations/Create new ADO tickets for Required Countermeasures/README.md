**Script Description**

The following script uses python with a number of basic packages, namely the requests module.
This script has the task of creating new Azure DevOps tickets when a condition is met. In this scenario, the condition is that the ticket is required. This can be customised to your needs.
This script also has the functionality of being able to programatticaly set Azure Devops Custom Fields if this is a task we need.  


**Config**

Located in the config.py file, we can specify the configuration for this script.
Set the domain name for your iriusrisk application and it's associated apitoken key.
Set the organisation and project name for your Azure DevOps board and provide it's associated issue type and personal access token.
If you wish to configure an azure devops custom field to be populated on ticket creation, inside ADOSetup.py please specify the field (e.g. ADO_CF) and pass the appropriate value inside the ADO_POST.py

**Usage**

Once configured, we can run the script to execute the operation, creating new tickets in ADO for all required countermeasures. This will link the new issue back into the project. 
Please ensure your IriusRisk project is already configured to Azure DevOps as the Issue Tracker provider, if you want the linkage to work as expected. Incorrectly configured projects will correctly create issues, but the linkage will not work.
You may feel the need to schedule this task to run automatically to meet your needs.

# Purpose

This collects the aggregate risk of a project and any project components within that project

# Requirements

1. Project components need to have the same name as the project they are referencing (the name of the project component is being used to perform subsequent API calls)
2. Python 3.11 or greater
3. Python Requests

# How to run

Call the script "get_risk_scores.py" and provide the following arguments "project_name", the "sub_domain" of your instance, and the "api_key". 

Example - 

pip3 install requests

python3 get_risk_scores.py aa james-rabe api-key


# Final Output

The final output should display the residual risk for each project and project component and the "Average Residual Risk: xx.xx" which represents the Residual risk of the project and the projects of the project components found in this project. 


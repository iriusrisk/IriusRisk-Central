# Purpose 

The purpose of this script is to assist with the bulk import of users from a CSV file. 

# Requirements

1. Import the requirements

```python
pip install -r requirements.txt
```
2. Create a spreadsheet with the following columns. 

firstName, lastName, email, username, role

Each row will contain the information for each user. 

# Process

Running this script requires three arguments. 

1. Sub-domain of the IriusRisk tenant
2. API Key for a user account that has the access required for creating users. 
3. The file location of the CSV with the user information. 

### Example - 
```python
python .\import_users.py <domain> <api_key> <file_location>
```

### Output - 
If successful, the response should say "<username> was created" and "Password reset email sent to <username>"

Each user will also receive an email requesting that they reset their password. 
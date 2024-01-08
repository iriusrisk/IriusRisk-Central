import requests
import json
import argparse
import pandas as pd


def import_users(sub_domain, api_key, file):

    user_information = pd.read_csv(file)

    for _, row in user_information.iterrows():
        firstName = str(row['firstName'])
        lastName = str(row['lastName'])
        email = str(row['email'])
        username = str(row['username'])
        role = str(row['role'])

        #v2_url = f"https://{sub_domain}.iriusrisk.com/api/v2/users"
        v1_url = f"https://{sub_domain}.iriusrisk.com/api/v1/users"

        payload = json.dumps({
            "auth": "saml",
            "email": email,
            "firstName": firstName,
            "lastName": lastName,
            "roleGroups": [role],
            #"password": "ChangeMe@Once24",
            #"passwordExpired": "true",
            "username": username
        })
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'api-token': api_key
        }

        response = requests.post(v1_url, headers=headers, data=payload)

        if response.status_code == 201:
            print(f"{username} was created")

        else:
            print(f"{username} was not created")
            print(response.text)

        url = f"https://{sub_domain}.iriusrisk.com/api/v2/users/{username}/reset-password-email/send"

        payload = {}
        headers = {
            'Accept': 'application/hal+json',
            'api-token': api_key
        }

        pwd_email_response = requests.post(url, headers=headers, data=payload)

        if pwd_email_response.status_code == 200:
            print(f"Password reset email was sent to {username}")

        else:
            print(f"Password reset email failed for {username}")
            print(pwd_email_response.text)


def main():
    parser = argparse.ArgumentParser(description="Bulk import of users")
    parser.add_argument("sub_domain", help="Sub-Domain to add the users to")
    parser.add_argument("api_key", help="API_key for the user creating the sub_domains")
    parser.add_argument("file", help="file location for users")

    args = parser.parse_args()

    # Call your function with command line arguments
    import_users(args.sub_domain, args.api_key, args.file)


if __name__ == "__main__":
    main()

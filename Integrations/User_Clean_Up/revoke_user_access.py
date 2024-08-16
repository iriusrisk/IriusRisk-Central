import tkinter as tk
from tkinter import ttk
import argparse
import requests
from datetime import datetime, timedelta, timezone
from config import API_TOKEN, INSTANCE_NAME, inactive_days

class Config:
    def __init__(self):
        self.API_TOKEN = API_TOKEN
        self.INSTANCE_NAME = INSTANCE_NAME
        self.inactive_days = inactive_days

config = Config()

class BaseAPI:
    def __init__(self):
        self.api_token = config.API_TOKEN
        self.instance_domain = self.extract_subdomain(config.INSTANCE_NAME)

    def extract_subdomain(self, instance_name):
        if instance_name.startswith("http"):
            instance_name = instance_name.split("//")[-1]  # Remove http(s)://
        if "." in instance_name:
            return instance_name.split('.')[0]  # Return the subdomain part
        return instance_name  # Return as is if it doesn't contain a period

    def make_request(self, endpoint, params={}, method='GET', data=None):
        url = f'https://{self.instance_domain}.iriusrisk.com/api/v2/{endpoint}'
        headers = {
            'Accept': 'application/hal+json',
            'api-token': self.api_token
        }
        try:
            response = requests.get(url, headers=headers, params=params)
            if method == 'DELETE':
                response = requests.delete(url, headers=headers, data=data)
            response.raise_for_status()
            return response.json()
        except requests.HTTPError as e:
            print(f"HTTP Error: {e.response.status_code} for URL: {e.response.url}")
            return None
        except requests.RequestException as e:
            print(f"Error: {e}")
            return None

    def fetch_all_users(self):
        url = f"https://{self.instance_domain}.iriusrisk.com/api/v2/users"
        headers = {
            'Accept': 'application/hal+json',
            'api-token': self.api_token
        }
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            users = data['_embedded']['items']
            return users
        else:
            print(f"Failed to fetch users: {response.status_code}")
            return []

class UserReport(BaseAPI):
    def get_active_users_within_days(self, days):
        end_date = datetime.now(timezone.utc)
        start_date = end_date - timedelta(days=days)
        start_date_str = start_date.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'

        filter_value = f"'timestamp'>='{start_date_str}':AND:'eventType'='LOGIN_SUCCESS'"
        params = {
            'filter': filter_value,
            'sort': 'timestamp',
            'size': 500
        }
        response = self.make_request('audit-logs', params=params)
        unique_usernames = set()  # Use a set to store unique usernames
        if response and '_embedded' in response and 'items' in response['_embedded']:
            for item in response['_embedded']['items']:
                unique_usernames.add(item['username'])  # Add each username to the set

        # Convert the set of unique usernames back to the list of dictionaries format
        unique_active_users = [{'username': username} for username in unique_usernames]
        return unique_active_users

    def identify_inactive_users(self, all_users, active_users):
        active_usernames = {user['username'] for user in active_users}
        return [user for user in all_users if user['username'] not in active_usernames]


    def delete_inactive_users(self, inactive_users):
        today = datetime.now().strftime("%Y-%m-%d")
        filename = f"Removed Users - {today}.txt"
        removed_users = []

        for user in inactive_users:
            url = f"https://{self.instance_domain}.iriusrisk.com/api/v1/users/{user['username']}"
            headers = {
                'Accept': 'application/json',
                'api-token': self.api_token
            }
            response = requests.delete(url, headers=headers)
            if response.status_code == 204:
                removed_users.append(user['username'])
                print(f"Deleted user: {user['username']}")
            else:
                print(f"Failed to delete user: {user['username']} Status Code: {response.status_code}")

        # Writing the removed users to a file
        with open(filename, 'w') as file:
            file.write("Removed Users on " + today + ":\n")
            for user in removed_users:
                file.write(user + "\n")
        print(f"Removal log saved to {filename}")

        return filename
def display_users(window, users, title="Users"):
    top = tk.Toplevel(window)
    top.title(title)
    listbox = tk.Listbox(top)
    listbox.pack(fill=tk.BOTH, expand=True)
    for user in users:
        listbox.insert(tk.END, user['username'])

def main():
    parser = argparse.ArgumentParser(description="User management tool.")
    parser.add_argument('--cleanup', action='store_true', help='Automatically cleanup inactive users.')
    parser.add_argument('--report', action='store_true', help='Open the GUI for manual reporting and management.')
    args = parser.parse_args()

    if args.cleanup:
        user_report = UserReport()
        all_users = user_report.fetch_all_users()
        active_users = user_report.get_active_users_within_days(config.inactive_days)
        inactive_users = user_report.identify_inactive_users(all_users, active_users)
        user_report.delete_inactive_users(inactive_users)
    elif args.report:
        app = tk.Tk()
        app.title("User Management Tool")

        user_report = UserReport()

        def show_active_users():
            active_users = user_report.get_active_users_within_days(config.inactive_days)
            display_users(app, active_users, "Active Users")

        def show_inactive_users():
            all_users = user_report.fetch_all_users()
            active_users = user_report.get_active_users_within_days(config.inactive_days)
            inactive_users = user_report.identify_inactive_users(all_users, active_users)
            display_users(app, inactive_users, "Inactive Users")

        ttk.Button(app, text="Display Active Users", command=show_active_users).pack(fill=tk.X, padx=20, pady=10)
        ttk.Button(app, text="Display Inactive Users", command=show_inactive_users).pack(fill=tk.X, padx=20, pady=10)

        app.mainloop()

if __name__ == "__main__":
    main()

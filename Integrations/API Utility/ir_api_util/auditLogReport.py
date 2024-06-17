import os
import sys
import requests
import json
import pandas as pd
from datetime import datetime, timedelta
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

def read_config(config_path='config.json'):
    try:
        with open(config_path, 'r') as config_file:
            config = json.load(config_file)
            output_path = os.path.expanduser(config.get('output_path', '~/'))
            os.makedirs(output_path, exist_ok=True)
            return output_path
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error reading config file: {e}. Defaulting to home directory.")
        output_path = os.path.expanduser('~/')
        os.makedirs(output_path, exist_ok=True)
        return output_path

class BaseAPI:
    def __init__(self, api_token_path='~/ir/.ir_user_token', instance_domain_path='~/ir/ir_instance_domain'):
        self.api_token_path = os.path.expanduser(api_token_path)
        self.instance_domain_path = os.path.expanduser(instance_domain_path)
        self.api_token, self.instance_domain = self.read_credentials()
        self.session = self.create_session()

    def read_credentials(self):
        try:
            with open(self.api_token_path, 'r') as token_file:
                api_token = token_file.read().strip()
            with open(self.instance_domain_path, 'r') as domain_file:
                instance_domain = domain_file.read().strip()
            return api_token, instance_domain
        except FileNotFoundError as e:
            print(f"Error: {e}. Make sure the paths are correct.")
            sys.exit(1)

    def create_session(self):
        session = requests.Session()
        retry = Retry(
            total=5,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS"]
        )
        adapter = HTTPAdapter(max_retries=retry)
        session.mount("https://", adapter)
        session.mount("http://", adapter)
        return session

    def make_request(self, endpoint, params={}):
        url = f'https://{self.instance_domain}.iriusrisk.com/api/v2/{endpoint}'
        headers = {
            'Accept': 'application/hal+json',
            'api-token': self.api_token
        }
        try:
            response = self.session.get(url, headers=headers, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.HTTPError as e:
            print(f"HTTP Error: {e.response.status_code} for URL: {e.response.url}")
            return None
        except requests.RequestException as e:
            print(f"Error: {e}")
            return None

class AuditLogReport(BaseAPI):
    def __init__(self, api_token_path='~/ir/.ir_user_token', instance_domain_path='~/ir/ir_instance_domain'):
        super().__init__(api_token_path, instance_domain_path)
        self.output_path = read_config()

    def fetch_total_pages(self, log_type, days):
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        start_date_str = start_date.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'
        end_date_str = end_date.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'

        params = {
            'filter': f"('timestamp'>='{start_date_str}':AND:'timestamp'<='{end_date_str}'):AND:'eventType'='{log_type}'",
            'page': 0,
            'size': 2000  #2000 is the largest  page size
        }

        response = self.make_request('audit-logs', params=params)
        if response and 'page' in response:
            return response['page']['totalPages']
        return 0

    def fetch_audit_logs(self, log_type, days):
        total_pages = self.fetch_total_pages(log_type, days)
        print(f"Total pages for log type '{log_type}' from the last {days} days: {total_pages}")

        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        start_date_str = start_date.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'
        end_date_str = end_date.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'

        all_logs = []
        for page in range(total_pages):
            print(f"Fetching page {page + 1} of {total_pages} for log type '{log_type}'...")
            params = {
                'filter': f"('timestamp'>='{start_date_str}':AND:'timestamp'<='{end_date_str}'):AND:'eventType'='{log_type}'",
                'page': page,
                'size': 2000  #2000 is the largest  page size
            }
            response = self.make_request('audit-logs', params=params)
            if response and '_embedded' in response:
                logs = response['_embedded']['items']
                all_logs.extend(logs)

        print(f"Fetched {len(all_logs)} logs for type '{log_type}' from the last {days} days.")
        return all_logs

    def generate_reports(self):
        project_logs = []
        user_logs = {7: [], 14: [], 30: [], 90: [], 180: []}
        project_log_types = [
            "PROJECT_SETTINGS_SAVED", "PROJECTS_IMPORTED", "PROJECT_DIAGRAM_UPDATED", "PROJECT_UPDATED",
            "ISSUE_CREATED", "CONTROL_CREATED", "CONTROL_UPDATED",
            "CONTROL_APPLIED", "THREAT_CREATED", "THREAT_UPDATED", "THREAT_CONTROL_MITIGATION_UPDATED_MANUALLY",
            "THREAT_CONTROL_MITIGATION_UPDATED_AUTOMATICALLY"
        ]
        user_log_types = ["LOGIN_SUCCESS", "LOGIN_NO_USER", "LOGIN_WRONG_PASSWORD", "LOGIN_ACCOUNT_LOCKED", "LOGIN_ACCOUNT_DISABLED", "USER_LOGGEDOUT", "USER_LOGGED_OUT_BY_ADMIN", "USER_ENABLED", "USER_DISABLED"]

        print("Fetching project logs...")
        # Fetch project logs
        for log_type in project_log_types:
            logs = self.fetch_audit_logs(log_type, 180)  # Fetch logs for the last 6 months
            project_logs.extend(logs)

        print("Fetching user logs...")
        # Fetch user logs for different periods
        for days in user_logs.keys():
            for log_type in user_log_types:
                logs = self.fetch_audit_logs(log_type, days)
                user_logs[days].extend(logs)

        # Create dataframes
        print("Creating dataframes...")
        project_df = pd.DataFrame(project_logs)
        user_dfs = {days: pd.DataFrame(logs) for days, logs in user_logs.items()}

        # Save to Excel
        print("Saving reports to Excel...")
        with pd.ExcelWriter(os.path.join(self.output_path, 'audit_log_report.xlsx')) as writer:
            project_df.to_excel(writer, sheet_name='Project Activity', index=False)
            for days, df in user_dfs.items():
                sheet_name = f'User Activity {days} days'
                df.to_excel(writer, sheet_name=sheet_name, index=False)

        print(f"Reports saved to {os.path.join(self.output_path, 'audit_log_report.xlsx')}")

def main():
    print("Starting Audit Log Report generation...")
    report = AuditLogReport()
    report.generate_reports()
    print("Audit Log Report generation completed.")
    print("")

if __name__ == "__main__":
    main()

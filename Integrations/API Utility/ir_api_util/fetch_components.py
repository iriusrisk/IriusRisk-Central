import os
import sys
import json
import requests
import urllib.parse


def read_config(config_path='config.json'):
    try:
        with open(config_path, 'r') as config_file:
            config = json.load(config_file)
            output_path = os.path.expanduser(config.get('output_path', '~/'))
            os.makedirs(output_path, exist_ok=True)
            page_size = int(config.get('page_size', 2000))
            return output_path, page_size
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error reading config file: {e}. Defaulting to ~/ and size=2000")
        return os.path.expanduser('~/'), 2000


def read_credentials(token_path='~/ir/.ir_user_token', domain_path='~/ir/ir_instance_domain'):
    try:
        with open(os.path.expanduser(token_path), 'r') as token_file:
            api_token = token_file.read().strip()
        with open(os.path.expanduser(domain_path), 'r') as domain_file:
            instance_domain = domain_file.read().strip()
        return api_token, instance_domain
    except FileNotFoundError as e:
        print(f"Error: {e}. Make sure the credential files exist.")
        sys.exit(1)


def fetch_components(output_path, page_size, api_token, instance_domain, category_name=None):
    all_items = []
    page = 0
    headers = {
        "Accept": "application/hal+json",
        "Content-Type": "application/json",
        "api-token": api_token
    }

    # Build filter string
    if category_name:
        filter_clause = f"'category.name'='{category_name}'"
    else:
        filter_clause = "'category.name'<>'Deprecated'"
    encoded_filter = urllib.parse.quote(filter_clause)

    print(f"📡 Fetching components for category: {category_name or 'ALL (non-deprecated)'}")
    while True:
        url = (
            f"https://{instance_domain}.iriusrisk.com/api/v2/components"
            f"?filter={encoded_filter}&size={page_size}&page={page}"
        )
        try:
            print(f"🔄 Requesting page {page}...")
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            data = response.json()

            items = data.get("_embedded", {}).get("items", [])
            all_items.extend(items)

            page_info = data.get("page", {})
            if page >= page_info.get("totalPages", 1) - 1:
                break
            page += 1

        except requests.HTTPError as e:
            print(f"❌ HTTP Error: {e}\nResponse: {response.text[:300]}")
            break
        except requests.RequestException as e:
            print(f"❌ Request Error: {e}")
            break
        except Exception as e:
            print(f"❌ Unexpected Error: {e}")
            break

    file_path = os.path.join(output_path, "components.tmp")
    with open(file_path, "w") as f:
        json.dump(all_items, f, indent=2)
    print(f"✅ Saved {len(all_items)} components to: {file_path}")


if __name__ == "__main__":
    output_path, page_size = read_config()
    api_token, instance_domain = read_credentials()

    category_name = None
    if len(sys.argv) > 1:
        category_name = sys.argv[1]

    fetch_components(output_path, page_size, api_token, instance_domain, category_name)

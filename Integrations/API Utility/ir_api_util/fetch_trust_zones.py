import os
import sys
import json
import requests


def read_config(config_path='config.json'):
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
            output_path = os.path.expanduser(config.get('output_path', '~/'))
            os.makedirs(output_path, exist_ok=True)
            page_size = int(config.get('page_size', 2000))
            return output_path, page_size
    except Exception as e:
        print(f"Error reading config: {e}. Using default output path.")
        return os.path.expanduser('~/'), 2000


def read_credentials(token_path='~/ir/.ir_user_token', domain_path='~/ir/ir_instance_domain'):
    try:
        with open(os.path.expanduser(token_path), 'r') as token_file:
            api_token = token_file.read().strip()
        with open(os.path.expanduser(domain_path), 'r') as domain_file:
            instance_domain = domain_file.read().strip()
        return api_token, instance_domain
    except FileNotFoundError as e:
        print(f"❌ Error: {e}. Check credential file paths.")
        sys.exit(1)


def fetch_trust_zones(api_token, instance_domain, page_size):
    headers = {
        "Accept": "application/hal+json",
        "Content-Type": "application/json",
        "api-token": api_token
    }
    all_items = []
    page = 0

    print("📡 Fetching Trust Zones...")
    while True:
        url = f"https://{instance_domain}.iriusrisk.com/api/v2/trust-zones?size={page_size}&page={page}"
        try:
            print(f"🔄 Page {page}...")
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            data = response.json()
            items = data.get("_embedded", {}).get("items", [])
            all_items.extend(items)

            page_info = data.get("page", {})
            if page >= page_info.get("totalPages", 1) - 1:
                break
            page += 1
        except requests.RequestException as e:
            print(f"❌ Request failed: {e}")
            break

    return all_items


if __name__ == "__main__":
    output_path, page_size = read_config()
    api_token, instance_domain = read_credentials()

    trust_zones = fetch_trust_zones(api_token, instance_domain, page_size)
    file_path = os.path.join(output_path, "trust_zones.tmp")

    with open(file_path, "w") as f:
        json.dump(trust_zones, f, indent=2)

    print(f"✅ Saved {len(trust_zones)} trust zones to: {file_path}")

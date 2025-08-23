import os
import sys
import json
import requests


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


def fetch_threats_for_use_case(use_case_id, output_path, page_size, api_token, instance_domain):
    all_items = []
    page = 0
    headers = {
        "Accept": "application/hal+json",
        "Content-Type": "application/json",
        "api-token": api_token
    }

    print(f"📡 Fetching threats for use case ID: {use_case_id}")

    while True:
        url = (
            f"https://{instance_domain}.iriusrisk.com/api/v2/libraries/threats"
            f"?filter='useCase.id'='{use_case_id}'&size={page_size}&page={page}"
        )
        try:
            print(f"🔄 Page {page} ...")
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

    out_path = os.path.join(output_path, "use_case_threats.tmp")
    with open(out_path, "w") as f:
        json.dump(all_items, f, indent=2)
    print(f"\n✅ Saved {len(all_items)} threats to: {out_path}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("❌ Usage: python3 fetch_use_case_threats.py <use_case_id>")
        sys.exit(1)

    use_case_id = sys.argv[1]
    output_path, page_size = read_config()
    api_token, instance_domain = read_credentials()
    fetch_threats_for_use_case(use_case_id, output_path, page_size, api_token, instance_domain)

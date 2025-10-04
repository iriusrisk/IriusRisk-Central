#!/usr/bin/env python3
"""
Phase 1: Collect v1 deprecated components

This script queries the API to collect all components that contain 'Deprecated' in their name
and saves the id, referenceId, and name to v1_components.json
"""

import requests
import json
import os
import sys
from dotenv import load_dotenv

def get_api_config():
    """
    Get API configuration including headers and base URL
    """
    load_dotenv()
    api_token = os.getenv('API_TOKEN')
    subdomain = os.getenv('SUBDOMAIN')
    
    headers = {
        'Accept': 'application/hal+json',
        'api-token': api_token
    }
    
    base_url = f"https://{subdomain}.iriusrisk.com/api/v2"
    
    return headers, base_url

def get_api_headers():
    """
    Get API headers with token from environment (backwards compatibility)
    """
    headers, _ = get_api_config()
    return headers

def collect_v1_components():
    """
    Collect all v1 (deprecated) components from the API
    """
    headers, base_url = get_api_config()
    url = f"{base_url}/components?filter='name'~'Deprecated'&size=200000"
    #url = f"{base_url}/components?size=200000"
    
    print(f"🌐 Making API request to: {url}")
    
    try:
        response = requests.get(url, headers=headers, timeout=60)
        response.raise_for_status()
        
        print(f"✅ API response status: {response.status_code}")
        
        data = response.json()
        print(f"🔍 Response keys: {list(data.keys())}")
        
        # Check if _embedded exists and what's in it
        if '_embedded' in data:
            embedded = data['_embedded']
            print(f"🔍 _embedded keys: {list(embedded.keys())}")
            # Try both 'items' and 'component' keys
            components = embedded.get('items', embedded.get('component', []))
        else:
            print("⚠️  No '_embedded' key found in response")
            # Maybe components are directly in the response?
            components = data if isinstance(data, list) else []
        
        # Check pagination info
        page_info = data.get('page', {})
        if page_info:
            total_elements = page_info.get('totalElements', 'unknown')
            size = page_info.get('size', 'unknown')
            number = page_info.get('number', 'unknown')
            total_pages = page_info.get('totalPages', 'unknown')
            print(f"📊 API returned {len(components)} components (page {number + 1 if isinstance(number, int) else 'unknown'} of {total_pages})")
            print(f"📈 Pagination info: {size} per page, {total_elements} total elements")
            
            if isinstance(total_elements, int) and total_elements > len(components):
                print(f"⚠️  WARNING: There are {total_elements} total components but we only got {len(components)}")
                print("   This means the API has pagination limits. You may need to implement pagination.")
        else:
            print(f"📊 API returned {len(components)} components")
        
        # If we have components, show the structure of the first one
        if components and len(components) > 0:
            print(f"🔍 First component keys: {list(components[0].keys())}")
        
        return components
        
    except requests.exceptions.RequestException as e:
        print(f"❌ API request failed: {e}")
        return []
    except json.JSONDecodeError as e:
        print(f"❌ Failed to parse JSON response: {e}")
        return []
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return []

def save_to_json(components, filename):
    """
    Save components list to a JSON file
    """
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(components, f, indent=2, ensure_ascii=False)
        print(f"Successfully saved {len(components)} components to {filename}")
        return True
    except Exception as e:
        print(f"Error saving to {filename}: {e}")
        return False

def main():
    """
    Main function to execute Phase 1
    """
    print("=== Phase 1: Collecting v1 Deprecated Components ===")
    
    # Collect v1 components
    v1_components = collect_v1_components()
    
    if v1_components:
        # Save to v1_components.json
        output_file = 'v1_components.json'
        if save_to_json(v1_components, output_file):
            print(f"\n✅ Phase 1 completed successfully!")
            print(f"📁 Output: {output_file}")
            print(f"📊 Total v1 components collected: {len(v1_components)}")
            
            # Display first few components as preview
            if len(v1_components) > 0:
                print("\n📋 Preview of first component:")
                print(json.dumps(v1_components[0], indent=2))
        else:
            print("\n❌ Phase 1 failed: Could not save components to file")
            exit(1)
    else:
        print("\n❌ Phase 1 failed: No components were collected")
        exit(1)

if __name__ == "__main__":
    main()
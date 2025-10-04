#!/usr/bin/env python3
"""
Phase 2: Collect v2 components (non-deprecated)

This script queries the API to collect all components and then filters out
any components that contain 'Deprecated' in their name to build the v2 list.
Saves the id, referenceId, and name to v2_components.json
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

def collect_v2_components():
    """
    Collect all components from the API (which will be v2 components)
    """
    headers, base_url = get_api_config()
    url = f"{base_url}/components?size=200000"
    
    print(f"🌐 Making API request to: {url}")
    
    try:
        response = requests.get(url, headers=headers, timeout=60)
        response.raise_for_status()
        
        data = response.json()
        embedded = data.get('_embedded', {})
        components = embedded.get('items', embedded.get('component', []))
        
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

def filter_v2_components(all_components):
    """
    Filter out deprecated components to get v2 components
    Returns a list of v2 components with id, referenceId, and name
    """
    import re
    v2_components = []
    
    for component in all_components:
        component_name = component.get('name', '')
        
        # Filter out any components that contain 'deprecated' as a standalone word (case insensitive)
        # Use word boundary regex to avoid matching 'deprecated' within other words
        deprecated_pattern = r'\bdeprecated\b'
        if not re.search(deprecated_pattern, component_name, re.IGNORECASE):
            v2_component = {
                'id': component.get('id'),
                'referenceId': component.get('referenceId'),
                'name': component.get('name')
            }
            v2_components.append(v2_component)
    
    print(f"Filtered to {len(v2_components)} v2 (non-deprecated) components")
    return v2_components

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
    Main function to execute Phase 2
    """
    print("=== Phase 2: Collecting v2 (Non-Deprecated) Components ===")
    
    # Collect all components
    all_components = collect_v2_components()
    
    if all_components:
        # Filter to get v2 components (remove deprecated ones)
        v2_components = filter_v2_components(all_components)
        
        if v2_components:
            # Save to v2_components.json
            output_file = 'v2_components.json'
            if save_to_json(v2_components, output_file):
                print(f"\n✅ Phase 2 completed successfully!")
                print(f"📁 Output: {output_file}")
                print(f"📊 Total v2 components collected: {len(v2_components)}")
                
                # Display first few components as preview
                if len(v2_components) > 0:
                    print("\n📋 Preview of first component:")
                    print(json.dumps(v2_components[0], indent=2))
                    
                # Show statistics
                total_components = len(all_components)
                deprecated_components = total_components - len(v2_components)
                print(f"\n📈 Statistics:")
                print(f"   Total components: {total_components}")
                print(f"   Deprecated components filtered out: {deprecated_components}")
                print(f"   V2 components remaining: {len(v2_components)}")
            else:
                print("\n❌ Phase 2 failed: Could not save components to file")
                exit(1)
        else:
            print("\n❌ Phase 2 failed: No v2 components found after filtering")
            exit(1)
    else:
        print("\n❌ Phase 2 failed: No components were collected from API")
        exit(1)

if __name__ == "__main__":
    main()
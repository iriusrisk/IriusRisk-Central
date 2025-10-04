#!/usr/bin/env python3
"""
Phase 4a: Collect risk pattern IDs attached to v2 components

This script:
1. Loads the v1_v2_component_mappings.json file
2. For each matched pair, finds the risk patterns attached to the v2 component
3. Saves the collected risk patterns to matching_risk_patterns.json
4. Does NOT transfer anything yet - just collects the data
"""

import requests
import json
import os
import sys
from dotenv import load_dotenv
import time
import logging
from datetime import datetime

def load_mappings():
    """
    Load v1 to v2 component mappings
    """
    try:
        with open('v1_v2_component_mappings.json', 'r', encoding='utf-8') as f:
            mappings = json.load(f)
        
        # Filter only matched mappings
        matched_mappings = [m for m in mappings if m.get('mapping_status') == 'MATCHED' and m.get('v2_component')]
        
        print(f"Loaded {len(mappings)} total mappings")
        print(f"Found {len(matched_mappings)} matched v1-v2 pairs")
        return matched_mappings
        
    except FileNotFoundError:
        print("Error: v1_v2_component_mappings.json not found")
        print("Make sure you've completed Phase 3 first")
        return []
    except json.JSONDecodeError as e:
        print(f"Error parsing mappings file: {e}")
        return []

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
    Get API headers with token (backwards compatibility)
    """
    headers, _ = get_api_config()
    return headers

def load_component_ids():
    """
    Load component IDs from the v1_components.json and v2_components.json files
    Creates a lookup table for referenceId -> UUID mapping
    """
    component_lookup = {}
    
    try:
        # Load v1 components
        with open('v1_components.json', 'r', encoding='utf-8') as f:
            v1_components = json.load(f)
            
        for component in v1_components:
            ref_id = component.get('referenceId')
            uuid = component.get('id')
            
            if ref_id and uuid:
                component_lookup[ref_id] = {
                    'id': uuid,
                    'name': component.get('name'),
                    'referenceId': ref_id,
                    'type': 'v1'
                }
        
        print(f"Loaded {len(v1_components)} v1 components")
        
    except FileNotFoundError:
        print("Warning: v1_components.json not found")
    except Exception as e:
        print(f"Error loading v1 components: {e}")
    
    try:
        # Load v2 components
        with open('v2_components.json', 'r', encoding='utf-8') as f:
            v2_components = json.load(f)
            
        for component in v2_components:
            ref_id = component.get('referenceId')
            uuid = component.get('id')
            
            if ref_id and uuid:
                component_lookup[ref_id] = {
                    'id': uuid,
                    'name': component.get('name'),
                    'referenceId': ref_id,
                    'type': 'v2'
                }
        
        print(f"Loaded {len(v2_components)} v2 components")
        
    except FileNotFoundError:
        print("Warning: v2_components.json not found")
    except Exception as e:
        print(f"Error loading v2 components: {e}")
    
    print(f"Total component lookup table: {len(component_lookup)} components")
    return component_lookup

def find_component_risk_patterns(component_ref_id, component_lookup):
    """
    Find risk patterns attached to a component using the correct API endpoint:
    /api/v2/components/{id}/risk-patterns
    """
    if component_ref_id not in component_lookup:
        print(f"    ⚠️  Component not found in lookup: {component_ref_id}")
        return []
    
    component_info = component_lookup[component_ref_id]
    component_uuid = component_info['id']
    
    print(f"    Found component UUID: {component_uuid}")
    
    # Use the correct API endpoint to get risk patterns for this component
    risk_patterns = get_component_risk_patterns_direct(component_uuid)
    return risk_patterns

def get_component_risk_patterns_direct(component_uuid):
    """
    Get risk patterns directly from the component using the /risk-patterns endpoint
    """
    headers, base_url = get_api_config()
    
    # Use the correct endpoint with subdomain from environment
    url = f"{base_url}/components/{component_uuid}/risk-patterns?page=0&size=2000"
    
    try:
        print(f"    � Getting risk patterns from: {url}")
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        data = response.json()
        risk_patterns = []
        
        # Extract risk patterns from the response
        if '_embedded' in data and 'items' in data['_embedded']:
            items = data['_embedded']['items']
            print(f"    ✅ Found {len(items)} risk patterns")
            
            for item in items:
                risk_pattern = {
                    'id': item.get('id'),  # This is the risk pattern ID we need
                    'name': item.get('name'),
                    'referenceId': item.get('referenceId'),
                    'description': item.get('description', ''),
                    'library': item.get('library', {}),
                    'source_component_id': component_uuid
                }
                
                risk_patterns.append(risk_pattern)
                print(f"      - {risk_pattern['name']} (ID: {risk_pattern['id']})")
        else:
            print(f"    ℹ️  No risk patterns found for component")
        
        return risk_patterns
        
    except requests.exceptions.RequestException as e:
        print(f"    ❌ Error getting risk patterns: {e}")
        return []
    except Exception as e:
        print(f"    ❌ Unexpected error: {e}")
        return []

def get_risk_pattern_details(risk_pattern_url):
    """
    Get risk pattern details from a specific URL
    Following plan.md structure
    """
    headers = get_api_headers()
    
    try:
        print(f"    📋 Getting risk pattern details from: {risk_pattern_url}")
        response = requests.get(risk_pattern_url, headers=headers)
        response.raise_for_status()
        
        data = response.json()
        
        # Extract risk pattern details as shown in plan.md
        risk_pattern = {
            'id': data.get('id'),
            'referenceId': data.get('referenceId'),
            'name': data.get('name'),
            'description': data.get('description', ''),
            'source_url': risk_pattern_url
        }
        
        print(f"    ✅ Found risk pattern: {risk_pattern['name']} (ID: {risk_pattern['id']})")
        return risk_pattern
        
    except requests.exceptions.RequestException as e:
        print(f"    ❌ Error getting risk pattern details: {e}")
        return None
    except Exception as e:
        print(f"    ❌ Unexpected error: {e}")
        return None

def collect_risk_patterns(mappings, component_lookup, max_mappings=None):
    """
    Collect risk patterns from v2 components (no transfers yet)
    """
    matching_risk_patterns = []
    
    # Limit processing for testing
    mappings_to_process = mappings[:max_mappings] if max_mappings else mappings
    
    print(f"Collecting risk patterns from {len(mappings_to_process)} matched mappings...")
    
    for i, mapping in enumerate(mappings_to_process):
        print(f"\n[{i+1}/{len(mappings_to_process)}] Processing mapping:")
        
        v1_component = mapping['v1_component']
        v2_component = mapping['v2_component']
        
        print(f"  V1: {v1_component.get('name', 'Unknown')} ({v1_component['referenceId']})")
        print(f"  V2: {v2_component['name']} ({v2_component['referenceId']})")
        
        # Find risk patterns attached to v2 component
        v2_risk_patterns = find_component_risk_patterns(v2_component['referenceId'], component_lookup)
        
        # Store the mapping info (even if no risk patterns found)
        risk_pattern_mapping = {
            'v1_component': v1_component,
            'v2_component': v2_component,
            'risk_patterns': v2_risk_patterns,
            'risk_patterns_count': len(v2_risk_patterns),
            'collection_timestamp': time.time()
        }
        
        if v2_risk_patterns:
            print(f"  📋 Found {len(v2_risk_patterns)} risk patterns in v2 component")
            for rp in v2_risk_patterns:
                print(f"    - {rp['name']} (ID: {rp['id']})")
        else:
            print(f"  ℹ️  No risk patterns found for v2 component")
        
        matching_risk_patterns.append(risk_pattern_mapping)
        
        # Rate limiting
        time.sleep(0.3)
    
    # Summary statistics
    total_risk_patterns = sum(len(m['risk_patterns']) for m in matching_risk_patterns)
    components_with_patterns = sum(1 for m in matching_risk_patterns if len(m['risk_patterns']) > 0)
    
    print(f"\n📊 Collection Summary:")
    print(f"   Total mappings processed: {len(matching_risk_patterns)}")
    print(f"   Components with risk patterns: {components_with_patterns}")
    print(f"   Components without risk patterns: {len(matching_risk_patterns) - components_with_patterns}")
    print(f"   Total risk patterns collected: {total_risk_patterns}")
    
    return matching_risk_patterns

def save_risk_patterns(risk_patterns, filename):
    """
    Save risk patterns mapping to JSON file
    """
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(risk_patterns, f, indent=2, ensure_ascii=False)
        print(f"Successfully saved risk patterns to {filename}")
        return True
    except Exception as e:
        print(f"Error saving to {filename}: {e}")
        return False

def main():
    """
    Main function to execute Phase 4a (collection only)
    """
    print("=== Phase 4a: Collect Risk Pattern IDs from v2 Components ===")
    
    # Load mappings
    mappings = load_mappings()
    if not mappings:
        exit(1)
    
    # Load component IDs from JSON files (referenceId -> UUID mapping)
    component_lookup = load_component_ids()
    if not component_lookup:
        print("❌ Failed to load component IDs from JSON files")
        exit(1)
    
    # Check if this is a test run
    test_mode = len(sys.argv) > 1 and sys.argv[1] == "--test"
    max_mappings = 10 if test_mode else None
    
    if test_mode:
        print(f"\n🧪 TEST MODE: Processing only {max_mappings} components for faster execution")
        print(f"📋 Starting risk pattern collection for {min(len(mappings), max_mappings or len(mappings))} v2 components...")
    else:
        print(f"\n📋 Starting risk pattern collection for ALL {len(mappings)} v2 components...")
        print(f"This will process all matched v1-v2 pairs to collect risk patterns.")
    
    matching_risk_patterns = collect_risk_patterns(mappings, component_lookup, max_mappings=max_mappings)
    
    if matching_risk_patterns:
        # Save risk patterns mapping
        output_file = 'matching_risk_patterns.json'
        if save_risk_patterns(matching_risk_patterns, output_file):
            print(f"\n✅ Phase 4a completed successfully!")
            print(f"📁 Output: {output_file}")
            
            # Show preview of components with risk patterns
            components_with_patterns = [m for m in matching_risk_patterns if len(m['risk_patterns']) > 0]
            if components_with_patterns:
                print(f"\n📋 Preview of first component with risk patterns:")
                preview = components_with_patterns[0]
                preview_data = {
                    'v1_component': preview['v1_component']['referenceId'],
                    'v2_component': preview['v2_component']['referenceId'],
                    'risk_patterns': [
                        {
                            'name': rp['name'],
                            'id': rp['id'],
                            'referenceId': rp['referenceId']
                        } for rp in preview['risk_patterns']
                    ]
                }
                print(json.dumps(preview_data, indent=2))
        else:
            print("\n❌ Phase 4a failed: Could not save risk patterns to file")
    else:
        print("\n❌ Phase 4a failed: No risk patterns were collected")

if __name__ == "__main__":
    main()
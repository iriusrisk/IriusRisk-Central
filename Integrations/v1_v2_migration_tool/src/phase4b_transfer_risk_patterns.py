#!/usr/bin/env python3
"""
Phase 4b: Transfer v2 risk patterns to v1 components

This script:
1. Loads the matching_risk_patterns.json file from Phase 4a
2. For each v1-v2 mapping with risk patterns, adds the v2 risk patterns to the v1 component
3. Uses the POST API: /api/v2/components/{v1_component_id}/risk-patterns
4. Tracks success/failure for each transfer
"""

import requests
import json
import os
import sys
from dotenv import load_dotenv
import time
import logging
from datetime import datetime

def get_api_config():
    """
    Get API configuration including headers and base URL
    """
    load_dotenv()
    api_token = os.getenv('API_TOKEN')
    subdomain = os.getenv('SUBDOMAIN')
    

    headers = {
        'Accept': 'application/hal+json',
        'Content-Type': 'application/json',
        'api-token': api_token
    }
    
    base_url = f"https://{subdomain}.iriusrisk.com/api/v2"
    
    return headers, base_url

def setup_logging():
    """
    Setup logging to both console and file
    """
    # Create logger
    logger = logging.getLogger('phase4b')
    logger.setLevel(logging.INFO)
    
    # Clear any existing handlers
    logger.handlers.clear()
    
    # Create formatters
    file_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    console_formatter = logging.Formatter('%(levelname)s - %(message)s')
    
    # File handler
    file_handler = logging.FileHandler('action.log')
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(file_formatter)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(console_formatter)
    
    # Add handlers to logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

def load_risk_pattern_mappings():
    """
    Load the risk pattern mappings from Phase 4a
    """
    try:
        # Use absolute path to ensure we find the file regardless of working directory
        file_path = os.path.join(os.getcwd(), 'matching_risk_patterns.json')
        print(f"Looking for risk patterns file at: {file_path}")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            mappings = json.load(f)
        
        print(f"Loaded {len(mappings)} risk pattern mappings")
        
        # Filter to only mappings that have risk patterns
        mappings_with_patterns = [m for m in mappings if len(m.get('risk_patterns', [])) > 0]
        print(f"Found {len(mappings_with_patterns)} mappings with risk patterns to transfer")
        
        return mappings_with_patterns
        
    except FileNotFoundError:
        print("Error: matching_risk_patterns.json not found")
        print("Make sure you've completed Phase 4a first")
        exit(1)
    except json.JSONDecodeError as e:
        print(f"Error parsing risk patterns file: {e}")
        exit(1)

def load_v1_component_ids():
    """
    Load v1 component IDs to get the UUIDs for the POST API calls
    """
    try:
        with open('v1_components.json', 'r', encoding='utf-8') as f:
            v1_components = json.load(f)
        
        # Create lookup table: referenceId -> UUID
        v1_lookup = {}
        for component in v1_components:
            ref_id = component.get('referenceId')
            uuid = component.get('id')
            
            if ref_id and uuid:
                v1_lookup[ref_id] = {
                    'id': uuid,
                    'name': component.get('name'),
                    'referenceId': ref_id
                }
        
        print(f"Loaded {len(v1_lookup)} v1 component IDs for lookup")
        return v1_lookup
        
    except FileNotFoundError:
        print("Error: v1_components.json not found")
        return {}
    except Exception as e:
        print(f"Error loading v1 components: {e}")
        return {}

def get_api_headers():
    """
    Get API headers with token
    """
    load_dotenv()
    api_token = os.getenv('API_TOKEN')
    subdomain = os.getenv('SUBDOMAIN')

    return {
        'Content-Type': 'application/json',
        'Accept': 'application/hal+json',
        'api-token': api_token
    }

def add_risk_pattern_to_component(v1_component_id, risk_pattern_id, risk_pattern_name, logger):
    """
    Add a risk pattern to a v1 component using the POST API
    """
    headers, base_url = get_api_config()

    url = f"{base_url}/components/{v1_component_id}/risk-patterns"

    payload = {
        "riskPattern": {
            "id": risk_pattern_id
        }
    }
    
    try:
        logger.info(f"POST {url} - Adding risk pattern '{risk_pattern_name}' (ID: {risk_pattern_id})")
        print(f"    🔄 Adding risk pattern '{risk_pattern_name}' (ID: {risk_pattern_id})")
        
        response = requests.post(url, headers=headers, json=payload)
        
        if response.status_code in [200, 201, 204]:
            logger.info(f"SUCCESS: Added risk pattern '{risk_pattern_name}' to component {v1_component_id}")
            print(f"    ✅ Successfully added risk pattern")
            return True, None
        else:
            error_msg = f"HTTP {response.status_code}: {response.text}"
            logger.error(f"FAILED: {error_msg} - Pattern: '{risk_pattern_name}' Component: {v1_component_id}")
            print(f"    ❌ Failed to add risk pattern: {error_msg}")
            return False, error_msg
            
    except requests.exceptions.RequestException as e:
        error_msg = f"Request error: {e}"
        logger.error(f"REQUEST_ERROR: {error_msg} - Pattern: '{risk_pattern_name}' Component: {v1_component_id}")
        print(f"    ❌ Error adding risk pattern: {error_msg}")
        return False, error_msg
    except Exception as e:
        error_msg = f"Unexpected error: {e}"
        logger.error(f"UNEXPECTED_ERROR: {error_msg} - Pattern: '{risk_pattern_name}' Component: {v1_component_id}")
        print(f"    ❌ Unexpected error: {error_msg}")
        return False, error_msg

def transfer_risk_patterns(mappings, v1_lookup, logger, max_mappings=None):
    """
    Transfer risk patterns from v2 to v1 components
    """
    transfer_results = []
    total_successful = 0
    total_failed = 0
    total_risk_patterns = 0
    
    # Limit processing for testing if specified
    mappings_to_process = mappings[:max_mappings] if max_mappings else mappings
    
    logger.info(f"=== PHASE 4B TRANSFER START === Processing {len(mappings_to_process)} mappings")
    print(f"Transferring risk patterns for {len(mappings_to_process)} component mappings...")
    
    for i, mapping in enumerate(mappings_to_process):
        print(f"\n[{i+1}/{len(mappings_to_process)}] Processing mapping:")
        
        v1_component = mapping['v1_component']
        v2_component = mapping['v2_component']
        risk_patterns = mapping['risk_patterns']
        
        print(f"  V1: {v1_component.get('name', 'Unknown')} ({v1_component['referenceId']})")
        print(f"  V2: {v2_component['name']} ({v2_component['referenceId']})")
        print(f"  Risk patterns to transfer: {len(risk_patterns)}")
        
        # Get v1 component UUID
        v1_ref_id = v1_component['referenceId']
        
        if v1_ref_id not in v1_lookup:
            print(f"  ⚠️  V1 component UUID not found for {v1_ref_id}")
            transfer_results.append({
                'v1_component': v1_component,
                'v2_component': v2_component,
                'status': 'FAILED',
                'error': 'V1 component UUID not found',
                'transfers': []
            })
            continue
        
        v1_uuid = v1_lookup[v1_ref_id]['id']
        print(f"  V1 UUID: {v1_uuid}")
        
        # Transfer each risk pattern
        transfer_details = []
        mapping_successful = 0
        mapping_failed = 0
        
        for rp in risk_patterns:
            success, error = add_risk_pattern_to_component(
                v1_uuid, 
                rp['id'], 
                rp['name'],
                logger
            )
            
            transfer_detail = {
                'risk_pattern_id': rp['id'],
                'risk_pattern_name': rp['name'],
                'success': success,
                'error': error
            }
            transfer_details.append(transfer_detail)
            
            if success:
                mapping_successful += 1
                total_successful += 1
            else:
                mapping_failed += 1
                total_failed += 1
            
            total_risk_patterns += 1
            
            # Longer rate limiting between API calls
            time.sleep(1.0)
        
        # Record results for this mapping
        transfer_results.append({
            'v1_component': v1_component,
            'v2_component': v2_component,
            'status': 'COMPLETED' if mapping_failed == 0 else 'PARTIAL',
            'successful_transfers': mapping_successful,
            'failed_transfers': mapping_failed,
            'transfers': transfer_details,
            'timestamp': time.time()
        })
        
        logger.info(f"MAPPING_COMPLETE: V1={v1_ref_id} -> {mapping_successful} successful, {mapping_failed} failed")
        print(f"  📊 Mapping result: {mapping_successful} successful, {mapping_failed} failed")
        
        # Longer rate limiting between component mappings
        time.sleep(2.0)
    
    print(f"\n📊 Overall Transfer Summary:")
    print(f"   Total mappings processed: {len(mappings_to_process)}")
    print(f"   Total risk patterns transferred: {total_risk_patterns}")
    print(f"   Successful transfers: {total_successful}")
    print(f"   Failed transfers: {total_failed}")
    print(f"   Success rate: {(total_successful/total_risk_patterns*100):.1f}%" if total_risk_patterns > 0 else "   Success rate: N/A")
    
    return transfer_results

def save_transfer_results(results, filename):
    """
    Save transfer results to JSON file
    """
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        print(f"Transfer results saved to {filename}")
        return True
    except Exception as e:
        print(f"Error saving results to {filename}: {e}")
        return False

def main():
    """
    Main function to execute Phase 4b (risk pattern transfer)
    """
    # Setup logging
    logger = setup_logging()
    
    logger.info("=== PHASE 4B START ===")
    print("=== Phase 4b: Transfer v2 Risk Patterns to v1 Components ===")
    
    # Load risk pattern mappings from Phase 4a
    mappings = load_risk_pattern_mappings()
    if not mappings:
        logger.error("Failed to load risk pattern mappings")
        return
    
    # Load v1 component IDs for API calls
    v1_lookup = load_v1_component_ids()
    if not v1_lookup:
        print("❌ Failed to load v1 component IDs")
        return
    
    # Ask user for confirmation before proceeding with full transfer
    total_transfers = sum(len(m.get('risk_patterns', [])) for m in mappings)
    print(f"\n⚠️  About to transfer {total_transfers} risk patterns across {len(mappings)} component mappings")
    print(f"This will make {total_transfers} POST API calls to add risk patterns to v1 components.")
    
    # Process ALL component mappings
    print(f"\n� Processing ALL {len(mappings)} component mappings...")
    print(f"This will transfer all v2 risk patterns to their corresponding v1 components.")
    
    # Transfer risk patterns for all mappings
    transfer_results = transfer_risk_patterns(mappings, v1_lookup, logger, max_mappings=None)
    
    if transfer_results:
        # Save results
        output_file = 'phase4b_transfer_results.json'
        if save_transfer_results(transfer_results, output_file):
            logger.info(f"Phase 4b completed successfully. Results saved to {output_file}")
            print(f"\n✅ Phase 4b completed!")
            print(f"📁 Results saved to: {output_file}")
            print(f"📝 Full log saved to: action.log")
            
            # Show summary
            successful_mappings = sum(1 for r in transfer_results if r['status'] == 'COMPLETED')
            partial_mappings = sum(1 for r in transfer_results if r['status'] == 'PARTIAL')
            
            logger.info(f"FINAL_SUMMARY: {successful_mappings} fully successful, {partial_mappings} partial, {len(transfer_results)} total")
            print(f"\n📈 Mapping Summary:")
            print(f"   Fully successful mappings: {successful_mappings}")
            print(f"   Partially successful mappings: {partial_mappings}")
            print(f"   Total mappings processed: {len(transfer_results)}")
        else:
            logger.error("Failed to save transfer results")
            print("\n❌ Phase 4b failed: Could not save transfer results")
    else:
        logger.error("No transfers were completed")
        print("\n❌ Phase 4b failed: No transfers were completed")
    
    logger.info("=== PHASE 4B END ===")

if __name__ == "__main__":
    main()
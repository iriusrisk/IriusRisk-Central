#!/usr/bin/env python3
"""
Phase 4 Cleanup: Undo risk pattern transfers

This script:
1. Reads the phase4b_transfer_results.json file
2. For each successful risk pattern transfer, performs a DELETE request to remove it
3. Uses the DELETE API: /api/v2/components/{v1_component_id}/risk-patterns/{risk_pattern_id}
4. Logs all cleanup actions to cleanup.log
"""

import requests
import json
import os
from dotenv import load_dotenv
import time
import logging
from datetime import datetime

def setup_logging():
    """
    Setup logging for cleanup operations
    """
    # Create logger
    logger = logging.getLogger('phase4_cleanup')
    logger.setLevel(logging.INFO)
    
    # Clear any existing handlers
    logger.handlers.clear()
    
    # Create formatters
    file_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    console_formatter = logging.Formatter('%(levelname)s - %(message)s')
    
    # File handler
    file_handler = logging.FileHandler('cleanup.log')
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

def load_transfer_results():
    """
    Load the transfer results from Phase 4b
    """
    try:
        with open('phase4b_transfer_results.json', 'r', encoding='utf-8') as f:
            results = json.load(f)
        
        print(f"Loaded {len(results)} transfer result records")
        
        # Count successful transfers to clean up
        successful_transfers = []
        for result in results:
            if result.get('transfers'):
                for transfer in result['transfers']:
                    if transfer.get('success', False):
                        successful_transfers.append({
                            'v1_component': result['v1_component'],
                            'transfer_detail': transfer
                        })
        
        print(f"Found {len(successful_transfers)} successful transfers to clean up")
        return successful_transfers
        
    except FileNotFoundError:
        print("Error: phase4b_transfer_results.json not found")
        print("Make sure you've run Phase 4b first")
        return []
    except json.JSONDecodeError as e:
        print(f"Error parsing transfer results file: {e}")
        return []

def load_v1_component_ids():
    """
    Load v1 component IDs to get the UUIDs for the DELETE API calls
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

def remove_risk_pattern_from_component(v1_component_id, risk_pattern_id, risk_pattern_name, logger):
    """
    Remove a risk pattern from a v1 component using the DELETE API
    """
    headers, base_url = get_api_config()
    
    # DELETE endpoint format: /api/v2/components/{component_id}/risk-patterns/{risk_pattern_id}
    url = f"{base_url}/components/{v1_component_id}/risk-patterns/{risk_pattern_id}"
    
    try:
        logger.info(f"DELETE {url} - Removing risk pattern '{risk_pattern_name}' (ID: {risk_pattern_id})")
        print(f"    🗑️  Removing risk pattern '{risk_pattern_name}' (ID: {risk_pattern_id})")
        
        response = requests.delete(url, headers=headers)
        
        if response.status_code in [200, 204, 404]:  # 404 might mean already removed
            if response.status_code == 404:
                logger.warning(f"ALREADY_REMOVED: Risk pattern '{risk_pattern_name}' not found on component {v1_component_id}")
                print(f"    ⚠️  Risk pattern already removed or not found")
            else:
                logger.info(f"SUCCESS: Removed risk pattern '{risk_pattern_name}' from component {v1_component_id}")
                print(f"    ✅ Successfully removed risk pattern")
            return True, None
        else:
            error_msg = f"HTTP {response.status_code}: {response.text}"
            logger.error(f"FAILED: {error_msg} - Pattern: '{risk_pattern_name}' Component: {v1_component_id}")
            print(f"    ❌ Failed to remove risk pattern: {error_msg}")
            return False, error_msg
            
    except requests.exceptions.RequestException as e:
        error_msg = f"Request error: {e}"
        logger.error(f"REQUEST_ERROR: {error_msg} - Pattern: '{risk_pattern_name}' Component: {v1_component_id}")
        print(f"    ❌ Error removing risk pattern: {error_msg}")
        return False, error_msg
    except Exception as e:
        error_msg = f"Unexpected error: {e}"
        logger.error(f"UNEXPECTED_ERROR: {error_msg} - Pattern: '{risk_pattern_name}' Component: {v1_component_id}")
        print(f"    ❌ Unexpected error: {error_msg}")
        return False, error_msg

def cleanup_risk_patterns(successful_transfers, v1_lookup, logger, max_cleanups=None):
    """
    Clean up (remove) risk patterns that were previously transferred
    """
    cleanup_results = []
    total_successful = 0
    total_failed = 0
    
    # Limit processing for testing if specified
    transfers_to_process = successful_transfers[:max_cleanups] if max_cleanups else successful_transfers
    
    logger.info(f"=== CLEANUP START === Processing {len(transfers_to_process)} transfers")
    print(f"Cleaning up {len(transfers_to_process)} successful risk pattern transfers...")
    
    # Group by component for better logging
    component_groups = {}
    for transfer in transfers_to_process:
        v1_ref_id = transfer['v1_component']['referenceId']
        if v1_ref_id not in component_groups:
            component_groups[v1_ref_id] = []
        component_groups[v1_ref_id].append(transfer)
    
    for i, (v1_ref_id, transfers) in enumerate(component_groups.items()):
        print(f"\n[{i+1}/{len(component_groups)}] Cleaning up component: {v1_ref_id}")
        
        # Get v1 component UUID
        if v1_ref_id not in v1_lookup:
            print(f"  ⚠️  V1 component UUID not found for {v1_ref_id}")
            logger.warning(f"V1 component UUID not found: {v1_ref_id}")
            continue
        
        v1_uuid = v1_lookup[v1_ref_id]['id']
        v1_name = v1_lookup[v1_ref_id].get('name', 'Unknown')
        
        print(f"  Component: {v1_name} ({v1_ref_id})")
        print(f"  UUID: {v1_uuid}")
        print(f"  Risk patterns to remove: {len(transfers)}")
        
        component_successful = 0
        component_failed = 0
        transfer_details = []
        
        # Remove each risk pattern
        for transfer in transfers:
            transfer_detail = transfer['transfer_detail']
            risk_pattern_id = transfer_detail['risk_pattern_id']
            risk_pattern_name = transfer_detail['risk_pattern_name']
            
            success, error = remove_risk_pattern_from_component(
                v1_uuid,
                risk_pattern_id,
                risk_pattern_name,
                logger
            )
            
            cleanup_detail = {
                'risk_pattern_id': risk_pattern_id,
                'risk_pattern_name': risk_pattern_name,
                'cleanup_success': success,
                'error': error
            }
            transfer_details.append(cleanup_detail)
            
            if success:
                component_successful += 1
                total_successful += 1
            else:
                component_failed += 1
                total_failed += 1
            
            # Rate limiting between DELETE calls
            time.sleep(0.5)
        
        # Record results for this component
        cleanup_results.append({
            'v1_component': transfers[0]['v1_component'],
            'successful_cleanups': component_successful,
            'failed_cleanups': component_failed,
            'cleanup_details': transfer_details,
            'timestamp': time.time()
        })
        
        logger.info(f"COMPONENT_CLEANUP_COMPLETE: {v1_ref_id} -> {component_successful} successful, {component_failed} failed")
        print(f"  📊 Component cleanup: {component_successful} successful, {component_failed} failed")
        
        # Rate limiting between components
        time.sleep(1.0)
    
    print(f"\n📊 Overall Cleanup Summary:")
    print(f"   Total components processed: {len(component_groups)}")
    print(f"   Successful removals: {total_successful}")
    print(f"   Failed removals: {total_failed}")
    print(f"   Success rate: {(total_successful/(total_successful+total_failed)*100):.1f}%" if (total_successful+total_failed) > 0 else "   Success rate: N/A")
    
    return cleanup_results

def save_cleanup_results(results, filename):
    """
    Save cleanup results to JSON file
    """
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        print(f"Cleanup results saved to {filename}")
        return True
    except Exception as e:
        print(f"Error saving cleanup results to {filename}: {e}")
        return False

def main():
    """
    Main function to execute Phase 4 cleanup
    """
    # Setup logging
    logger = setup_logging()
    
    logger.info("=== PHASE 4 CLEANUP START ===")
    print("=== Phase 4 Cleanup: Remove Transferred Risk Patterns ===")
    
    # Load successful transfers from Phase 4b
    successful_transfers = load_transfer_results()
    if not successful_transfers:
        logger.error("No successful transfers found to clean up")
        return
    
    # Load v1 component IDs for API calls
    v1_lookup = load_v1_component_ids()
    if not v1_lookup:
        logger.error("Failed to load v1 component IDs")
        print("❌ Failed to load v1 component IDs")
        return
    
    # Ask user for confirmation
    print(f"\n⚠️  About to REMOVE {len(successful_transfers)} risk patterns from v1 components")
    print(f"This will undo the transfers made in Phase 4b")
    print(f"📝 All cleanup actions will be logged to cleanup.log")
    
    # Process ALL successful transfers
    print(f"\n� Processing ALL {len(successful_transfers)} transferred risk patterns...")
    print(f"This will remove all risk patterns that were added in Phase 4b.")
    
    # Cleanup risk patterns for all transfers
    cleanup_results = cleanup_risk_patterns(successful_transfers, v1_lookup, logger, max_cleanups=None)
    
    if cleanup_results:
        # Save results
        output_file = 'phase4_cleanup_results.json'
        if save_cleanup_results(cleanup_results, output_file):
            logger.info(f"Phase 4 cleanup completed. Results saved to {output_file}")
            print(f"\n✅ Phase 4 cleanup completed!")
            print(f"📁 Results saved to: {output_file}")
            print(f"📝 Full log saved to: cleanup.log")
            
            # Show summary
            total_cleanups = sum(r['successful_cleanups'] + r['failed_cleanups'] for r in cleanup_results)
            successful_cleanups = sum(r['successful_cleanups'] for r in cleanup_results)
            
            logger.info(f"CLEANUP_SUMMARY: {successful_cleanups}/{total_cleanups} successful removals")
            print(f"\n📈 Cleanup Summary:")
            print(f"   Components processed: {len(cleanup_results)}")
            print(f"   Risk patterns removed: {successful_cleanups}")
            print(f"   Failed removals: {total_cleanups - successful_cleanups}")
        else:
            logger.error("Failed to save cleanup results")
            print("\n❌ Cleanup failed: Could not save cleanup results")
    else:
        logger.error("No cleanups were completed")
        print("\n❌ Cleanup failed: No cleanups were completed")
    
    logger.info("=== PHASE 4 CLEANUP END ===")

if __name__ == "__main__":
    main()
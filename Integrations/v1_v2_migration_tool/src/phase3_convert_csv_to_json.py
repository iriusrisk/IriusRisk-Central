#!/usr/bin/env python3
"""
Phase 3 (Alternative): Convert existing CSV mappings to JSON format

This script reads the existing v1_v2_component_mappings.csv file and converts it
to the JSON format needed for Phase 4: v1_v2_component_mappings.json
"""

import csv
import json
import os
from typing import List, Dict, Any, Optional

def load_csv_mappings() -> List[Dict[str, Any]]:
    """
    Load mappings from the existing CSV file
    """
    mappings: List[Dict[str, Any]] = []
    
    try:
        with open('v1_v2_component_mappings.csv', 'r', encoding='utf-8') as f:
            # Read the first line to clean up headers
            first_line = f.readline().strip()
            # Remove trailing comma and extra spaces
            clean_header = first_line.rstrip(',').strip()
            
            # Reset file pointer and create reader with cleaned header
            f.seek(0)
            content = f.read()
            lines = content.split('\n')
            lines[0] = clean_header
            
            # Create a string buffer for DictReader
            from io import StringIO
            clean_content = '\n'.join(lines)
            reader = csv.DictReader(StringIO(clean_content))
            
            for row in reader:
                # Skip empty rows
                if not any(row.values()):
                    continue
                    
                # Clean up the values
                cleaned_row = {}
                for key, value in row.items():
                    if key:  # Skip None keys
                        clean_key = key.strip()
                        cleaned_row[clean_key] = value.strip() if value and value.strip() else None
                
                # Check if migration status is "yes" and v2 component exists
                migrated_value = cleaned_row.get("Migrated?", "")
                migrated = migrated_value.lower() == "yes" if migrated_value else False
                v2_name = cleaned_row.get("V2 Component name")
                v2_ref = cleaned_row.get("V2 Component ref")
                
                # Build the complete mapping dictionary with proper structure
                if migrated and v2_name and v2_ref:
                    mapping = {
                        "v1_component": {
                            "name": cleaned_row.get("V1 Component name"),
                            "referenceId": cleaned_row.get("V1 Component ref"),
                            "category": cleaned_row.get("V1 Component category")
                        },
                        "v2_component": {
                            "name": v2_name,
                            "referenceId": v2_ref,
                            "category": cleaned_row.get("V2 Component category")
                        },
                        "mapping_status": "MATCHED",
                        "migrated": migrated,
                        "has_icon": cleaned_row.get("Does it has icon?", "") != ""
                    }
                else:
                    mapping = {
                        "v1_component": {
                            "name": cleaned_row.get("V1 Component name"),
                            "referenceId": cleaned_row.get("V1 Component ref"),
                            "category": cleaned_row.get("V1 Component category")
                        },
                        "v2_component": None,
                        "mapping_status": "NO_MATCH",
                        "migrated": migrated,
                        "has_icon": cleaned_row.get("Does it has icon?", "") != ""
                    }
                
                mappings.append(mapping)
        
        print(f"Successfully loaded {len(mappings)} mappings from CSV")
        return mappings
        
    except FileNotFoundError:
        print("Error: v1_v2_component_mappings.csv not found")
        return []
    except Exception as e:
        print(f"Error reading CSV file: {e}")
        return []

def save_mappings_to_json(mappings: List[Dict[str, Any]], filename: str) -> bool:
    """
    Save mappings to JSON file
    """
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(mappings, f, indent=2, ensure_ascii=False)
        print(f"Successfully saved {len(mappings)} mappings to {filename}")
        return True
    except Exception as e:
        print(f"Error saving to {filename}: {e}")
        return False

def analyze_mappings(mappings: List[Dict[str, Any]]) -> None:
    """
    Analyze and display statistics about the mappings
    """
    total = len(mappings)
    matched = sum(1 for m in mappings if m['mapping_status'] == 'MATCHED')
    no_match = total - matched
    
    print(f"\n📈 Mapping Statistics:")
    print(f"   Total components: {total}")
    print(f"   Successfully matched (migrated): {matched}")
    print(f"   No v2 equivalent yet: {no_match}")
    print(f"   Migration completion rate: {(matched/total*100):.1f}%")
    
    # Show categories with no matches
    no_match_categories = set()
    for mapping in mappings:
        if mapping['mapping_status'] == 'NO_MATCH':
            category = mapping['v1_component']['category']
            if category:  # Only add non-None categories
                no_match_categories.add(category)
    
    if no_match_categories:
        print(f"\n📋 Categories with unmigrated components:")
        for category in sorted(no_match_categories):
            count = sum(1 for m in mappings 
                       if m['mapping_status'] == 'NO_MATCH' 
                       and m['v1_component']['category'] == category)
            print(f"   {category}: {count} components")

def main():
    """
    Main function to execute Phase 3 alternative
    """
    print("=== Phase 3: Converting CSV Mappings to JSON ===")
    
    # Load mappings from CSV
    mappings = load_csv_mappings()
    
    if not mappings:
        print("❌ No mappings loaded from CSV file")
        return
    
    # Analyze the mappings
    analyze_mappings(mappings)
    
    # Save to JSON format for Phase 4
    output_file = 'v1_v2_component_mappings.json'
    if save_mappings_to_json(mappings, output_file):
        print(f"\n✅ Phase 3 completed successfully!")
        print(f"📁 Output: {output_file}")
        
        # Show preview of first matched and unmatched mapping
        matched_example = next((m for m in mappings if m['mapping_status'] == 'MATCHED'), None)
        unmatched_example = next((m for m in mappings if m['mapping_status'] == 'NO_MATCH'), None)
        
        if matched_example:
            print(f"\n📋 Example of matched mapping:")
            print(json.dumps(matched_example, indent=2))
        
        if unmatched_example:
            print(f"\n📋 Example of unmatched mapping:")
            print(json.dumps(unmatched_example, indent=2))
    else:
        print("\n❌ Phase 3 failed: Could not save mappings to JSON file")

if __name__ == "__main__":
    main()
#!/usr/bin/env python3
"""
IriusRisk Custom Fields Builder

This script creates custom field types and custom fields in IriusRisk.
Configuration is loaded from environment variables via .env file.

Author: IriusRisk Integration Team
"""

import os
import sys
import json
import requests
from dotenv import load_dotenv
from typing import Dict, List, Optional, Any, cast
from pathlib import Path

# Load environment variables
load_dotenv()

# Configuration (support multiple env var names for flexibility)
IRIUSRISK_URL = os.getenv("IRIUSRISK_URL") or os.getenv("IRIUSRISK_DOMAIN") or os.getenv("IRIUSRISK_HOST")
API_TOKEN = os.getenv("API_TOKEN") or os.getenv("IRIUSRISK_API_TOKEN")

if not IRIUSRISK_URL or not API_TOKEN:
    print("ERROR: Missing required environment variables.")
    print("Please ensure IRIUSRISK_URL (or IRIUSRISK_DOMAIN) and API_TOKEN (or IRIUSRISK_API_TOKEN) are set in your .env file.")
    sys.exit(1)

# Remove trailing slash from URL if present
IRIUSRISK_URL = cast(str, IRIUSRISK_URL).rstrip('/')
API_TOKEN = cast(str, API_TOKEN)

# API Endpoints
BASE_API_URL = f"{IRIUSRISK_URL}/api/v2"
CUSTOM_FIELD_TYPES_URL = f"{BASE_API_URL}/custom-fields/types"
CUSTOM_FIELDS_URL = f"{BASE_API_URL}/custom-fields"


class IriusRiskCustomFieldsBuilder:
    """Main class for building custom field types and custom fields in IriusRisk."""
    
    def __init__(self, api_token: str, base_url: str):
        """
        Initialize the builder.
        
        Args:
            api_token: IriusRisk API token
            base_url: Base URL for the API
        """
        self.api_token = api_token
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            "api-token": self.api_token,
            "Content-Type": "application/json",
            "Accept": "application/hal+json"
        })
    
    def create_custom_field_type(self, name: str, description: str = "", 
                                  multi_selectable: bool = False) -> Optional[Dict[str, Any]]:
        """
        Create a custom field type.
        
        Args:
            name: Name of the custom field type
            description: Description of the custom field type
            multi_selectable: Whether multiple values can be selected
            
        Returns:
            Response data if successful, None otherwise
        """
        payload = {
            "name": name,
            "description": description,
            "multiSelectable": multi_selectable
        }
        
        try:
            response = self.session.post(
                f"{self.base_url}/custom-fields/types",
                json=payload
            )
            response.raise_for_status()
            result = response.json()
            print(f"✓ Created custom field type: {name} (ID: {result.get('id')})")
            return result
        except requests.exceptions.HTTPError as e:
            print(f"✗ Failed to create custom field type '{name}': {e}")
            if e.response.text:
                print(f"  Error details: {e.response.text}")
            return None
        except Exception as e:
            print(f"✗ Unexpected error creating custom field type '{name}': {e}")
            return None
    
    def get_custom_field_types(self, filter_query: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get all custom field types.
        
        Args:
            filter_query: Optional filter query
            
        Returns:
            List of custom field types
        """
        try:
            params = {}
            if filter_query:
                params['filter'] = filter_query
                
            response = self.session.get(
                f"{self.base_url}/custom-fields/types",
                params=params
            )
            response.raise_for_status()
            result = response.json()
            
            # Handle paginated response
            if '_embedded' in result and 'items' in result['_embedded']:
                return result['_embedded']['items']
            return []
        except Exception as e:
            print(f"✗ Failed to get custom field types: {e}")
            return []

    def get_custom_field_type_values(self, type_id: str,
                                     filter_query: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get values for a custom field type.
        """
        try:
            params = {}
            if filter_query:
                params['filter'] = filter_query

            response = self.session.get(
                f"{self.base_url}/custom-fields/types/{type_id}/values",
                params=params
            )
            response.raise_for_status()
            result = response.json()

            if '_embedded' in result and 'items' in result['_embedded']:
                return result['_embedded']['items']
            return []
        except Exception as e:
            print(f"✗ Failed to get custom field type values: {e}")
            return []
    
    def find_custom_field_type_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Find a custom field type by name.
        
        Args:
            name: Name of the custom field type
            
        Returns:
            Custom field type data if found, None otherwise
        """
        # Use server-side filter to avoid pagination misses
        filter_query = f"'name'='{name}'"
        types_list = self.get_custom_field_types(filter_query=filter_query)
        for field_type in types_list:
            if field_type.get('name') == name:
                return field_type
        return None

    def find_custom_field_by_reference(self, reference_id: str) -> Optional[Dict[str, Any]]:
        """
        Find a custom field by referenceId.
        """
        filter_query = f"'referenceId'='{reference_id}'"
        fields_list = self.get_custom_fields(filter_query=filter_query)
        for field in fields_list:
            if field.get('referenceId') == reference_id:
                return field
        return None
    
    def create_custom_field(self, name: str, reference_id: str, entity: str,
                           type_id: str, description: str = "",
                           required: bool = False, visible: bool = True,
                           editable: bool = True, exportable: bool = True,
                           default_value: Optional[str] = None,
                           max_size: Optional[int] = None,
                           regex_validator: Optional[str] = None,
                           group_id: Optional[str] = None,
                           after: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Create a custom field.
        
        Args:
            name: Name of the custom field
            reference_id: Unique reference ID for the custom field
            entity: Entity type (project, countermeasure, test, threat)
            type_id: UUID of the custom field type
            description: Description of the custom field
            required: Whether the field is required
            visible: Whether the field is visible
            editable: Whether the field is editable
            exportable: Whether the field is exportable
            default_value: Default value for the field
            max_size: Maximum size for field values
            regex_validator: Regex pattern for validation
            group_id: UUID of the custom field group
            after: UUID of the custom field to position after
            
        Returns:
            Response data if successful, None otherwise
        """
        # Validate entity
        valid_entities = ['project', 'countermeasure', 'test', 'threat']
        if entity not in valid_entities:
            print(f"✗ Invalid entity '{entity}'. Must be one of: {', '.join(valid_entities)}")
            return None
        
        payload = {
            "name": name,
            "referenceId": reference_id,
            "entity": entity,
            "typeId": type_id,
            "description": description,
            "required": required,
            "visible": visible,
            "editable": editable,
            "exportable": exportable
        }
        
        # Add optional fields
        if default_value is not None:
            payload["defaultValue"] = default_value
        if max_size is not None:
            payload["maxSize"] = max_size
        if regex_validator is not None:
            payload["regexValidator"] = regex_validator
        if group_id is not None:
            payload["groupId"] = group_id
        if after is not None:
            payload["after"] = after
        
        try:
            response = self.session.post(
                f"{self.base_url}/custom-fields",
                json=payload
            )
            response.raise_for_status()
            result = response.json()
            print(f"✓ Created custom field: {name} (ID: {result.get('id')}) for {entity}")
            return result
        except requests.exceptions.HTTPError as e:
            print(f"✗ Failed to create custom field '{name}': {e}")
            if e.response.text:
                print(f"  Error details: {e.response.text}")
            return None
        except Exception as e:
            print(f"✗ Unexpected error creating custom field '{name}': {e}")
            return None
    
    def get_custom_fields(self, filter_query: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get all custom fields.
        
        Args:
            filter_query: Optional filter query
            
        Returns:
            List of custom fields
        """
        try:
            params = {}
            if filter_query:
                params['filter'] = filter_query
                
            response = self.session.get(
                f"{self.base_url}/custom-fields",
                params=params
            )
            response.raise_for_status()
            result = response.json()
            
            # Handle paginated response
            if '_embedded' in result and 'items' in result['_embedded']:
                return result['_embedded']['items']
            return []
        except Exception as e:
            print(f"✗ Failed to get custom fields: {e}")
            return []
    
    def add_custom_field_type_value(self, type_id: str, value: str,
                                     after: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Add a value to a custom field type.
        
        Args:
            type_id: UUID of the custom field type
            value: Value to add
            description: Description of the value
            after: Optional UUID of the value to insert after (ordering)
            
        Returns:
            Response data if successful, None otherwise
        """
        payload = {
            "value": value,
            "after": after  # API expects the property even if null
        }
        
        try:
            response = self.session.post(
                f"{self.base_url}/custom-fields/types/{type_id}/values",
                json=payload
            )
            response.raise_for_status()
            result = response.json()
            print(f"  ✓ Added value '{value}' to custom field type")
            return result
        except requests.exceptions.HTTPError as e:
            # Treat duplicate value as non-fatal (type already has this value)
            try:
                error_body = e.response.json()
                errors = error_body.get('errors', []) if isinstance(error_body, dict) else []
                for err in errors:
                    if err.get('type') == 'NonUniqueValue':
                        print(f"  ↷ Value '{value}' already exists; skipping")
                        return None
            except Exception:
                pass

            print(f"  ✗ Failed to add value '{value}': {e}")
            if e.response.text:
                print(f"    Error details: {e.response.text}")
            return None
        except Exception as e:
            print(f"  ✗ Unexpected error adding value '{value}': {e}")
            return None


def load_inputs_file(file_path: str = "inputs.json") -> Optional[Dict[str, Any]]:
    """
    Load the inputs JSON file.
    
    Args:
        file_path: Path to the inputs JSON file
        
    Returns:
        Parsed JSON data or None if failed
    """
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
        print(f"✓ Loaded configuration from {file_path}")
        return data
    except FileNotFoundError:
        print(f"✗ File not found: {file_path}")
        return None
    except json.JSONDecodeError as e:
        print(f"✗ Invalid JSON in {file_path}: {e}")
        return None
    except Exception as e:
        print(f"✗ Error loading {file_path}: {e}")
        return None


def build_builtin_type_lookup(builder: 'IriusRiskCustomFieldsBuilder') -> Dict[str, str]:
    """
    Build a lookup of built-in type names to their IDs from the API.
    Falls back to common uppercase names if API call fails.
    """
    lookup: Dict[str, str] = {}
    try:
        types = builder.get_custom_field_types()
        for t in types:
            name = str(t.get('name', '')).lower()
            t_id = t.get('id')
            if name and t_id:
                lookup[name] = t_id
    except Exception:
        pass

    # Fallback mapping by conventional names if API didn't populate
    fallback_names = ['text', 'textarea', 'link', 'user', 'group', 'date']
    for name in fallback_names:
        lookup.setdefault(name, name.upper())

    return lookup


def process_inputs_file(builder: 'IriusRiskCustomFieldsBuilder', 
                        inputs_data: Dict[str, Any]) -> Dict[str, List[str]]:
    """
    Process the inputs file and create custom field types and fields.
    
    Args:
        builder: IriusRiskCustomFieldsBuilder instance
        inputs_data: Parsed inputs JSON data
        
    Returns:
        Dictionary with created field IDs and any errors
    """
    results = {
        'created_types': [],
        'created_fields': [],
        'errors': []
    }
    
    # Get the intake form data
    intake_form = inputs_data.get('intake_form', {})
    form_name = intake_form.get('name', 'Custom Fields')
    form_description = intake_form.get('description', '')
    fields = intake_form.get('fields', [])
    
    if not fields:
        results['errors'].append("No fields found in inputs file")
        return results
    
    print(f"\nProcessing form: {form_name}")
    if form_description:
        print(f"Description: {form_description}")
    print(f"Total fields to create: {len(fields)}")
    print("=" * 80)
    
    # Build lookup for built-in types once
    builtin_types = build_builtin_type_lookup(builder)

    # First pass: Create custom field types for dropdown fields (or reuse existing)
    print("\n📋 Creating custom field types for dropdowns...")
    print("-" * 80)
    
    type_mapping = {}  # Maps field name to type ID
    
    for field in fields:
        field_name = field.get('name', '')
        field_label = field.get('label', field_name)
        field_type = field.get('type', '').lower()
        
        if field_type == 'dropdown':
            options = field.get('options', [])
            multi_select = field.get('multi_select', False)
            
            if not options:
                error_msg = f"Dropdown field '{field_label}' has no options"
                print(f"  ⚠️  {error_msg}")
                results['errors'].append(error_msg)
                continue
            
            # Create the custom field type
            type_name = f"{field_label}"
            type_description = field.get('notes', f"Options for {field_label}")
            # Try to find existing type by name to avoid duplicates
            existing_type = builder.find_custom_field_type_by_name(type_name)

            if existing_type:
                type_id = existing_type.get('id')
                type_mapping[field_name] = type_id
                print(f"  ↷ Reusing existing custom field type '{type_name}' (ID: {type_id})")
            else:
                field_type_result = builder.create_custom_field_type(
                    name=type_name,
                    description=type_description[:255] if len(type_description) > 255 else type_description,
                    multi_selectable=multi_select
                )

                if field_type_result:
                    type_id = field_type_result['id']
                    type_mapping[field_name] = type_id
                    results['created_types'].append(type_id)
                else:
                    error_msg = f"Failed to create type for '{field_label}'"
                    results['errors'].append(error_msg)
                    continue

            # Add values to the type, preserving order using 'after'
            if type_id:
                print(f"  Adding {len(options)} options to '{type_name}'...")

                # Load existing values to avoid duplicates and to get ordering anchor
                existing_values = builder.get_custom_field_type_values(type_id)
                existing_map = {v.get('value'): v.get('id') for v in existing_values if v.get('value') and v.get('id')}
                # Start ordering after the last existing value (if any)
                previous_value_id = existing_values[-1]['id'] if existing_values else None

                for option in options:
                    # Skip if already exists
                    if option in existing_map:
                        previous_value_id = existing_map[option]
                        print(f"  ↷ Value '{option}' already exists; skipping")
                        continue

                    value_resp = builder.add_custom_field_type_value(
                        type_id=type_id,
                        value=option,
                        after=previous_value_id
                    )
                    if value_resp and value_resp.get('id'):
                        previous_value_id = value_resp['id']
    
    # Second pass: Create custom fields
    print("\n📝 Creating custom fields...")
    print("-" * 80)
    
    for field in fields:
        field_name = field.get('name', '')
        field_label = field.get('label', field_name)
        field_type = field.get('type', '').lower()
        location = field.get('location', 'Project').lower()
        required = field.get('required', False)
        notes = field.get('notes', '')
        max_length = field.get('max_length')
        regex = field.get('regex')
        
        if not field_name:
            error_msg = "Field missing 'name' property"
            print(f"  ⚠️  {error_msg}")
            results['errors'].append(error_msg)
            continue
        
        # Determine the type ID
        if field_type == 'dropdown':
            # Use the custom type we created or reused
            type_id = type_mapping.get(field_name)
            if not type_id:
                error_msg = f"No type ID found for dropdown field '{field_label}'"
                print(f"  ⚠️  {error_msg}")
                results['errors'].append(error_msg)
                continue
        else:
            # Use built-in type lookup from API
            type_id = builtin_types.get(field_type)
            if not type_id:
                error_msg = f"Unknown field type '{field_type}' for field '{field_label}'"
                print(f"  ⚠️  {error_msg}")
                results['errors'].append(error_msg)
                continue

        # If field already exists (by referenceId), skip creation and record its id
        existing_field = builder.find_custom_field_by_reference(field_name)
        if existing_field and existing_field.get('id'):
            print(f"  ↷ Reusing existing custom field '{field_label}' (ID: {existing_field['id']})")
            results['created_fields'].append(existing_field['id'])
            continue

        # Create the custom field
        field_result = builder.create_custom_field(
            name=field_label,
            reference_id=field_name,
            entity=location,
            type_id=type_id,
            description=notes[:200000] if notes else "",
            required=required,
            visible=True,
            editable=True,
            exportable=True,
            max_size=max_length,
            regex_validator=regex
        )

        if field_result:
            results['created_fields'].append(field_result['id'])
        else:
            error_msg = f"Failed to create field '{field_label}'"
            results['errors'].append(error_msg)
    
    return results


def create_from_inputs_file(inputs_file: str = "inputs.json"):
    """
    Create custom fields from an inputs JSON file.
    
    Args:
        inputs_file: Path to the inputs JSON file
    """
    print("=" * 80)
    print("IriusRisk Custom Fields Builder - Batch Creation")
    print("=" * 80)
    print()
    
    # Load the inputs file
    inputs_data = load_inputs_file(inputs_file)
    if not inputs_data:
        print("\n❌ Failed to load inputs file. Exiting.")
        return False
    
    # Initialize the builder
    builder = IriusRiskCustomFieldsBuilder(API_TOKEN, BASE_API_URL)
    
    # Process the inputs file
    results = process_inputs_file(builder, inputs_data)
    
    # Print summary
    print("\n" + "=" * 80)
    print("📊 Creation Summary")
    print("=" * 80)
    print(f"✓ Custom field types created: {len(results['created_types'])}")
    print(f"✓ Custom fields created: {len(results['created_fields'])}")
    
    if results['errors']:
        print(f"⚠️  Errors encountered: {len(results['errors'])}")
        print("\nErrors:")
        for error in results['errors']:
            print(f"  - {error}")
    else:
        print("✓ All fields created successfully!")
    
    print("=" * 80)
    
    return len(results['errors']) == 0


def example_usage():
    """Example usage demonstrating how to create custom field types and fields."""
    
    print("=" * 80)
    print("IriusRisk Custom Fields Builder")
    print("=" * 80)
    print()
    
    # Initialize the builder
    builder = IriusRiskCustomFieldsBuilder(API_TOKEN, BASE_API_URL)
    
    # Example 1: Create a simple custom field type
    print("Creating custom field types...")
    print("-" * 80)
    
    priority_type = builder.create_custom_field_type(
        name="Priority Level",
        description="Priority levels for projects",
        multi_selectable=False
    )
    
    if priority_type:
        # Add values to the custom field type
        print("Adding values to Priority Level type...")
        builder.add_custom_field_type_value(priority_type['id'], "Critical", "Critical priority")
        builder.add_custom_field_type_value(priority_type['id'], "High", "High priority")
        builder.add_custom_field_type_value(priority_type['id'], "Medium", "Medium priority")
        builder.add_custom_field_type_value(priority_type['id'], "Low", "Low priority")
    
    print()
    
    # Example 2: Create a multi-select custom field type
    compliance_type = builder.create_custom_field_type(
        name="Compliance Frameworks",
        description="Applicable compliance frameworks",
        multi_selectable=True
    )
    
    if compliance_type:
        print("Adding values to Compliance Frameworks type...")
        builder.add_custom_field_type_value(compliance_type['id'], "ISO 27001", "ISO 27001 standard")
        builder.add_custom_field_type_value(compliance_type['id'], "SOC 2", "SOC 2 compliance")
        builder.add_custom_field_type_value(compliance_type['id'], "GDPR", "GDPR compliance")
        builder.add_custom_field_type_value(compliance_type['id'], "HIPAA", "HIPAA compliance")
        builder.add_custom_field_type_value(compliance_type['id'], "PCI-DSS", "PCI-DSS compliance")
    
    print()
    print("-" * 80)
    print("Creating custom fields...")
    print("-" * 80)
    
    # Example 3: Create custom fields using the types we just created
    if priority_type:
        builder.create_custom_field(
            name="Project Priority",
            reference_id="project-priority",
            entity="project",
            type_id=priority_type['id'],
            description="The priority level of this project",
            required=True,
            default_value="Medium"
        )
    
    if compliance_type:
        builder.create_custom_field(
            name="Required Compliance",
            reference_id="required-compliance",
            entity="project",
            type_id=compliance_type['id'],
            description="Compliance frameworks that apply to this project",
            required=False
        )
    
    print()
    print("=" * 80)
    print("Custom fields creation completed!")
    print("=" * 80)


def main():
    """Main entry point."""
    try:
        # Check if user wants to use inputs.json or run examples
        if len(sys.argv) > 1:
            if sys.argv[1] == '--example':
                print("Running example usage...\n")
                example_usage()
            elif sys.argv[1] == '--help':
                print("IriusRisk Custom Fields Builder")
                print("\nUsage:")
                print("  python build_custom_fields.py              # Create fields from inputs.json")
                print("  python build_custom_fields.py --example    # Run example demonstrations")
                print("  python build_custom_fields.py --file FILE  # Use custom input file")
                print("  python build_custom_fields.py --help       # Show this help message")
            elif sys.argv[1] == '--file' and len(sys.argv) > 2:
                create_from_inputs_file(sys.argv[2])
            else:
                print(f"Unknown argument: {sys.argv[1]}")
                print("Use --help for usage information")
        else:
            # Default: use inputs.json
            create_from_inputs_file()
    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\n\nUnexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

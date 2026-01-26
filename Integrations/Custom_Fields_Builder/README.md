# IriusRisk Custom Fields Builder

This script automates the creation of custom field types and custom fields in IriusRisk using the API v2.

## Overview

Custom fields in IriusRisk allow you to extend the data model for projects, threats, countermeasures, and tests with additional information specific to your organization's needs.

This tool provides:
- **Custom Field Types**: Define reusable field types with predefined values (dropdowns, multi-select)
- **Custom Fields**: Create fields attached to specific entities (project, threat, countermeasure, test)

## Prerequisites

- Python 3.7 or higher
- IriusRisk instance with API access
- API token with `SYSTEM_SETTINGS_UPDATE` permission

## Installation

1. Navigate to the Custom_Fields_Builder directory:
```bash
cd Custom_Fields_Builder
```

Create a virtual environment to install dependencies in

2. Install required dependencies:


Create a virtual environment and install dependencies

```bash

pythonx -m venv .venv && source .venv/bin/source #mac/linux
pythonx -m venv .venv && source .venv\Scripts\Activate.ps1 #windows

pip install -r requirements.txt
```

3. Create a `.env` file from the example:
```bash
cp .env.example .env
```

4. Edit the `.env` file with your credentials:
```env
IRIUSRISK_URL=https://your-instance.iriusrisk.com
API_TOKEN=your-api-token-here
```

5. (Optional) Customize the `inputs-threat-example.json` file with your desired custom fields, or use the provided example configuration.

## Configuration Files

### .env
Contains your IriusRisk connection credentials:
- `IRIUSRISK_URL`: Your IriusRisk instance URL
- `API_TOKEN`: API token with SYSTEM_SETTINGS_UPDATE permission

### inputs.json
Defines the custom field types and fields to create. The provided file includes a complete "Application Intake" form with 10 fields covering common intake requirements. You can modify this file or create your own following the same structure.

## Usage

### Basic Usage - Create from inputs.json

The primary way to use this tool is to define your custom fields in `inputs-threats-example.json` and run:

```bash
python build_custom_fields.py
```

This will automatically:
1. Read field definitions from `inputs-threats-example.json`
2. Create custom field types for dropdown fields
3. Add options/values to those types
4. Create all custom fields with proper configuration

### Command Line Options

```bash
# Create fields from inputs.json (default)
python build_custom_fields.py

# Create fields from a custom input file
python build_custom_fields.py --file inputs-threats-example.json.json

# Run example demonstrations
python build_custom_fields.py --example

# Show help
python build_custom_fields.py --help
```

### Input File Format

The script reads from `inputs-threats-example.json.json` with the following structure:

```json
{
  "intake_form": {
    "name": "Application Intake",
    "description": "Custom fields for application intake",
    "fields": [
      {
        "name": "field_reference_id",
        "label": "Field Display Name",
        "required": true,
        "location": "Project",
        "type": "text",
        "notes": "Description of the field",
        "max_length": 100,
        "regex": "^[a-zA-Z0-9]*$"
      },
      {
        "name": "dropdown_field",
        "label": "Dropdown Field",
        "required": false,
        "location": "Project",
        "type": "dropdown",
        "multi_select": true,
        "options": ["Option 1", "Option 2", "Option 3"],
        "notes": "Multi-select dropdown"
      }
    ]
  }
}
```

#### Field Properties:

- **name** (required): Unique reference ID for the field
- **label** (required): Display name shown to users
- **required** (boolean): Whether the field must be filled
- **location** (required): Entity type - `Project`, `Threat`, `Countermeasure`, or `Test`
- **type** (required): Field type - `text`, `textarea`, `dropdown`, `link`, `user`, `date`
- **notes** (optional): Description/help text for the field
- **max_length** (optional): Maximum character length for text/textarea fields
- **regex** (optional): Regular expression for validation
- **options** (required for dropdown): Array of dropdown options
- **multi_select** (optional for dropdown): Allow multiple selections (default: false)

### Custom Implementation

You can import and use the `IriusRiskCustomFieldsBuilder` class in your own scripts:

```python
from build_custom_fields import IriusRiskCustomFieldsBuilder
import os
from dotenv import load_dotenv

load_dotenv()

# Initialize builder
builder = IriusRiskCustomFieldsBuilder(
    api_token=os.getenv("API_TOKEN"),
    base_url=f"{os.getenv('IRIUSRISK_URL')}/api/v2"
)

# Create a custom field type
status_type = builder.create_custom_field_type(
    name="Project Status",
    description="Status of the project",
    multi_selectable=False
)

# Add values to the type
if status_type:
    builder.add_custom_field_type_value(
        type_id=status_type['id'],
        name="Planning",
        description="Project in planning phase"
    )
    builder.add_custom_field_type_value(
        type_id=status_type['id'],
        name="In Progress",
        description="Project actively being worked on"
    )
    builder.add_custom_field_type_value(
        type_id=status_type['id'],
        name="Completed",
        description="Project completed"
    )

    # Create a custom field using this type
    builder.create_custom_field(
        name="Current Status",
        reference_id="current-status",
        entity="project",
        type_id=status_type['id'],
        description="The current status of the project",
        required=True,
        default_value="Planning"
    )
```

## API Methods

### IriusRiskCustomFieldsBuilder

#### `create_custom_field_type(name, description="", multi_selectable=False)`
Creates a new custom field type.

**Parameters:**
- `name` (str): Name of the custom field type
- `description` (str): Description of the type
- `multi_selectable` (bool): Whether multiple values can be selected

**Returns:** Dict with the created type data or None if failed

#### `add_custom_field_type_value(type_id, name, description="")`
Adds a value to an existing custom field type.

**Parameters:**
- `type_id` (str): UUID of the custom field type
- `name` (str): Name of the value
- `description` (str): Description of the value

**Returns:** Dict with the created value data or None if failed

#### `create_custom_field(name, reference_id, entity, type_id, ...)`
Creates a new custom field.

**Parameters:**
- `name` (str): Name of the custom field
- `reference_id` (str): Unique reference ID
- `entity` (str): Entity type - one of: `project`, `countermeasure`, `test`, `threat`
- `type_id` (str): UUID of the custom field type
- `description` (str): Description of the field
- `required` (bool): Whether the field is required
- `visible` (bool): Whether the field is visible
- `editable` (bool): Whether the field is editable
- `exportable` (bool): Whether the field is exportable
- `default_value` (str): Default value for the field
- `max_size` (int): Maximum size for field values
- `regex_validator` (str): Regex pattern for validation
- `group_id` (str): UUID of custom field group
- `after` (str): UUID of field to position after

**Returns:** Dict with the created field data or None if failed

#### `get_custom_field_types(filter_query=None)`
Retrieves all custom field types.

**Returns:** List of custom field type dictionaries

#### `get_custom_fields(filter_query=None)`
Retrieves all custom fields.

**Returns:** List of custom field dictionaries

#### `find_custom_field_type_by_name(name)`
Finds a custom field type by its name.

**Returns:** Custom field type dictionary or None if not found

## Custom Field Entities

Custom fields can be attached to the following entities:
- `project` - Project-level custom fields
- `threat` - Threat-level custom fields
- `countermeasure` - Countermeasure-level custom fields
- `test` - Test-level custom fields

## Built-in Custom Field Types

IriusRisk provides several built-in field types:
- **TEXT**: Single-line text field
- **TEXTAREA**: Multi-line text field
- **DATE**: Date field (format: yyyy-MM-dd HH:mm:ss)
- **USER**: User selection field
- **GROUP**: Business unit selection field
- **LINK**: URL link field (format: NAME_::_URL)

You can also create your own custom types with predefined values.

**Output:**
```
================================================================================
IriusRisk Custom Fields Builder - Batch Creation
================================================================================

✓ Loaded configuration from inputs.json

Processing form: Application Intake
Description: Custom fields for application intake and threat modeling process
Total fields to create: 10
================================================================================

📋 Creating custom field types for dropdowns...
--------------------------------------------------------------------------------
✓ Created custom field type: Business Area (ID: abc-123...)
  ✓ Added value 'EPP (Enterprise Products and Platforms)' to custom field type
  ✓ Added value 'CPP (Commercial Products and Platforms)' to custom field type
  ✓ Added value 'Restaurants' to custom field type
✓ Created custom field type: User Base Information (ID: def-456...)
  ✓ Added value 'Consumer' to custom field type
  ✓ Added value 'Employee' to custom field type
  ✓ Added value 'Vendors & Third Parties' to custom field type
  ✓ Added value 'Franchisee & Crew Members' to custom field type
✓ Created custom field type: Initial Data Classification (ID: ghi-789...)
  ✓ Added value 'Public' to custom field type
  ✓ Added value 'McD Business Use' to custom field type
  ✓ Added value 'McD Restricted' to custom field type
  ✓ Added value 'McD Highly Restricted' to custom field type

📝 Creating custom fields...
--------------------------------------------------------------------------------
✓ Created custom field: Intake Request Number (ID: ...) for project
✓ Created custom field: System Description & Business Goals (ID: ...) for project
✓ Created custom field: Business Area (ID: ...) for project
✓ Created custom field: User Base Information (ID: ...) for project
✓ Created custom field: Initial Data Classification (ID: ...) for project
✓ Created custom field: Key Integrations (ID: ...) for project
✓ Created custom field: Known Constraints or Risks (ID: ...) for project
✓ Created custom field: Links to Existing Project Documentation (ID: ...) for project
✓ Created custom field: Business Owner (ID: ...) for project
✓ Created custom field: Architecture Owner (ID: ...) for project

================================================================================
📊 Creation Summary
================================================================================
✓ Custom field types created: 3
✓ Custom fields created: 10
✓ All fields created successfully!
================================================================================
```

## Error Handling

The script includes comprehensive error handling and will display:
- Success messages with created resource IDs
- Detailed error messages if creation fails
- HTTP response details for debugging

## Troubleshooting

### Authentication Errors
- Verify your API token is correct and has `SYSTEM_SETTINGS_UPDATE` permission
- Check that the IRIUSRISK_URL is correct (including https://)

### Creation Failures
- Ensure unique reference IDs for custom fields
- Verify the type_id exists before creating a custom field
- Check that entity values are valid: `project`, `threat`, `countermeasure`, or `test`

### Connection Issues
- Verify network connectivity to your IriusRisk instance
- Check firewall rules allow outbound HTTPS connections
- Ensure the instance URL is accessible

## License

This integration is provided under the IriusRisk Commercial License.

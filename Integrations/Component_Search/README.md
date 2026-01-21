# IriusRisk Component Search Tool

A Python tool to search for components in IriusRisk and identify all projects that use those components.

## Overview

This tool searches the IriusRisk API for components matching a search term (in either the component name or description) and displays all projects that use each matching component. Results are displayed in the terminal and saved to a timestamped text file.

## Features

- Search for components by name or description
- Case-insensitive search
- Groups results by match type:
  - Matched in Name Only
  - Matched in Description Only
  - Matched in Both Name and Description
- Lists all projects using each component
- Outputs to both terminal and text file
- Timestamped output files: `YYYYMMDD_searchterm.txt`

## Prerequisites

- Python 3.7+
- Access to an IriusRisk instance
- IriusRisk API token with appropriate permissions

## Installation

1. Clone or download this repository

2. Install required dependencies:
```bash
pip install -r requirements.txt
```

Or install individually:
```bash
pip install requests python-dotenv
```

## Configuration

Create a `.env` file in the project directory with your IriusRisk credentials:

```env
IRIUSRISK_DOMAIN=https://your-instance.iriusrisk.com
IRIUSRISK_API_TOKEN=your_api_token_here
```

There is also an example of that in the repo. 

```bash

cp .env.template .env

```

**Important:** Never commit the `.env` file to version control. It's already included in `.gitignore`.

### Getting Your API Token

1. Log in to your IriusRisk instance
2. Navigate to your user settings
3. Generate an API token
4. Copy the token to your `.env` file

## Usage

Basic syntax:
```bash
python3 search.py --search "search_term"
```

### Examples

Search for components containing "gps":
```bash
python3 search.py --search "gps"
```

Search for components containing "database":
```bash
python3 search.py --search "database"
```

Search for components containing "api":
```bash
python3 search.py --search "api"
```

## Output Format

### Terminal Output

The script displays results grouped by match type:

```
Search Results for 'gps': 3 component(s) found with projects

================================================================================

MATCHED IN NAME ONLY (2 component(s)):
--------------------------------------------------------------------------------
GPS Module | abc123-def456-ghi789 | projects=5
  - Project Alpha | proj-123
  - Project Beta | proj-456
  
POS Sync Agent | xyz789-abc123-def456 | projects=1
  - Retail System | proj-789

MATCHED IN DESCRIPTION ONLY (1 component(s)):
--------------------------------------------------------------------------------
Location Service | def456-ghi789-jkl012 | projects=3
  Description: A service that provides GPS coordinates and location tracking...
  - Mobile App | proj-321
  - Navigation System | proj-654
  
```

### File Output

Results are automatically saved to a text file named `YYYYMMDD_searchterm.txt` (e.g., `20260121_gps.txt`).

The file contains the same information displayed in the terminal.

## How It Works

1. Connects to the IriusRisk API using credentials from `.env`
2. Searches for components where the search term appears in:
   - Component name (case-insensitive)
   - Component description (case-insensitive)
3. For each matching component, retrieves all projects using that component
4. Groups and displays results by match type
5. Saves results to a timestamped text file

## Troubleshooting

### Authentication Error (401)
- Verify your `IRIUSRISK_API_TOKEN` is correct in the `.env` file
- Check that your API token hasn't expired
- Ensure your account has appropriate permissions

### Connection Error
- Verify your `IRIUSRISK_DOMAIN` is correct in the `.env` file
- Check your network connection
- Ensure the IriusRisk instance is accessible

### No Results Found
- Try a broader search term
- Verify components exist in your IriusRisk instance
- Check that the search term is spelled correctly

### Module Not Found Error
- Install required dependencies: `pip install -r requirements.txt`
- Verify you're using Python 3.7 or higher

## API Rate Limiting

The tool uses pagination (100 items per page) and waits for responses. If you encounter rate limiting:
- Reduce the frequency of searches
- Contact your IriusRisk administrator about API limits

## Output Files

Output files are stored in the same directory as the script and follow the naming convention:
- `YYYYMMDD_searchterm.txt`

Example: `20260121_gps.txt`

**Note:** These files are excluded from version control via `.gitignore`.

## License

This tool is provided as-is for use with IriusRisk instances.

## Support

For issues related to:
- **This tool**: Contact your organization's development team
- **IriusRisk API**: Refer to IriusRisk documentation or support
- **API access**: Contact your IriusRisk administrator

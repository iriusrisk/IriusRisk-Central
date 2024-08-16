# User Management Tool

## Overview
This Python script provides a comprehensive solution for monitoring active and stale user accounts via an API. It includes functionality for automated cleanup of inactive user accounts based on a set period of inactivity and a graphical user interface (GUI) for interactive user management and reporting.

## Features
- **Automated Cleanup**: Removes users who have not been active within a specified number of days.
- **Interactive GUI**: Offers a user-friendly interface to display active and inactive users.
- **Flexible Usage**: Can be operated via command-line arguments for automated tasks or used interactively with a GUI for reports.

## Requirements
- Python 3.x
- `requests` library
- Tkinter (usually included with Python)
- Proper API credentials and access permissions

## Configuration
Before running the script, ensure the API token, instance name, and inactivity threshold are correctly configured in a `config.py` file. This file should include:

```python
API_TOKEN = 'your_api_token_here'
INSTANCE_NAME = 'your_instance_name_here'
inactive_days = 90  # Adjust the number of days to define inactivity
```

## Installation
Install the necessary Python packages if they are not already installed:
```bash
pip install requests argparse
```

## Usage
The script supports two modes of operation:

1. **Cleanup Mode**:
   - Use this mode to automatically identify and delete inactive users.
   ```bash
   python3 revoke_user_access.py --cleanup
   ```

2. **Report Mode**:
   - This mode starts the GUI for manually viewing active and inactive users.
   ```bash
   python3 revoke_user_access.py --report
   ```

### GUI Operations
- **Display Active Users**: Shows a list of users who have been active within the specified inactive days.
- **Display Inactive Users**: Shows a list of users who have not been active within the specified inactive days.

## Deployment
Ensure that the script is deployed on a system with network access to the API. Adjust firewall settings if necessary to allow the script to make HTTP/HTTPS requests.

## Logging
- The script logs the results of the cleanup operations, including details of the deleted users, in a file named `Removed Users - <date>.txt`.

# Purpose 

The purpose of this script is to bulk update Jira issue tracker profiles in your IriusRisk instance. It allows you to:

- Update issue tracker URLs across multiple Jira configurations simultaneously
- Update Jira credentials (username and password) for all or specific trackers
- Export current tracker configurations as a backup before making changes
- Validate tracker connections after updates to ensure credentials are correct
- Publish draft configurations to live status

This is useful when migrating to a new Jira instance, rotating credentials, or updating connection URLs in bulk.

# Requirements

1. Set up the virtual environment

```bash
python3 -m venv jira-bulk-updater-env
```

Activate the virtual environment

```bash
source jira-bulk-updater-env/bin/activate
```

2. Clone the repo into this environment

```bash
git clone https://github.com/IriusRisk/IriusRisk-Central.git
```

Navigate to the 'Jira Bulk Updater' directory

```bash
cd Integrations/'Jira Bulk Updater'/
```

3. Create and configure the `config.json` file

Create a `config.json` file in the same directory with the following structure:

```json
{
  "instance_url": "https://your-instance.iriusrisk.com/",
  "api_token": "your-api-token-here"
}
```

Replace the values with:
- `instance_url`: Your IriusRisk instance URL (include trailing slash)
- `api_token`: Your IriusRisk API token for authentication

**Note:** The `config.json` file is in `.gitignore` to prevent accidentally committing credentials.

4. Install the required packages

```bash
pip install -r requirements.txt
```

Or manually install:

```bash
pip install requests rich
```

# Execution

The script supports several modes of operation via command-line arguments:

## Update Issue Tracker URLs

```bash
python3 jira-url-changer.py --url "https://new-jira-instance.atlassian.net/"
```

## Update Credentials (Username-Password Auth Only)

Update username only:
```bash
python3 jira-url-changer.py --username "new-username@example.com"
```

Update password only:
```bash
python3 jira-url-changer.py --password "new-password"
```

Update both username and password:
```bash
python3 jira-url-changer.py --username "new-username@example.com" --password "new-password"
```

## Combine URL and Credentials Updates

```bash
python3 jira-url-changer.py --url "https://new-jira-instance.atlassian.net/" --username "new-username@example.com" --password "new-password"
```

## Export Backup Only

Export current configurations without making any changes:

```bash
python3 jira-url-changer.py --export
```

## Validate Credentials After Updating

Test the connection and credentials for each updated tracker:

```bash
python3 jira-url-changer.py --url "https://new-jira-instance.atlassian.net/" --validate
```

## Enable Debug Output

See detailed information about what changes will be made:

```bash
python3 jira-url-changer.py --url "https://new-jira-instance.atlassian.net/" --debug
```

# Options

- `--url URL` - Update issue tracker URLs to the specified URL
- `--username USERNAME` - Update issue tracker username (username-password auth only)
- `--password PASSWORD` - Update issue tracker password (username-password auth only)
- `--export` - Export current configurations to backup file before updating
- `--validate` - Validate tracker credentials after updating
- `--debug` - Enable debug output showing detailed change information
- `--help` - Display help message

# Output

The script provides:

1. **Console Output** - Progress messages and status updates during execution with color-coded results:
   - Green for successful operations
   - Yellow for warnings (e.g., trackers skipped due to non-username/password auth)
   - Red for errors

2. **Backup File** (when using `--export`) - A JSON file named `tracker_backup_YYYYMMDD_HHMMSS.json` containing:
   - Timestamp of export
   - Count of trackers backed up
   - Complete configurations for all trackers

3. **Updated Configurations** - Changes are published to live status and available in your IriusRisk instance immediately after confirmation

# Notes

- The script will prompt for confirmation before making any updates
- Only Jira issue trackers are processed; other tracker types are skipped
- Credential updates only work with username-password authentication; token-based auth trackers are skipped
- Always use `--export` to create a backup before making bulk updates
- Use `--validate` to test connectivity after updates

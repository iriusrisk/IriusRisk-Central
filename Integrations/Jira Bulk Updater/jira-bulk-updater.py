import sys
import json
import argparse
import os
import requests
from rich import print
from rich.prompt import Prompt

def load_config(config_file='config.json'):
    """
    Load API credentials and instance URL from a configuration file.
    
    Args:
        config_file: Path to the JSON config file
    
    Returns:
        Tuple of (instance_url, api_token)
    
    Raises:
        SystemExit: If config file not found or required keys are missing
    """
    if not os.path.exists(config_file):
        print(f"[red][ERROR] Configuration file not found: {config_file}[/red]")
        print(f"[yellow]Please create a {config_file} file with the following structure:[/yellow]")
        print("""
{
  "instance_url": "https://your-instance.iriusrisk.com/",
  "api_token": "your-api-token-here"
}
        """)
        sys.exit(1)
    
    try:
        with open(config_file, 'r') as f:
            config = json.load(f)
    except json.JSONDecodeError as e:
        print(f"[red][ERROR] Invalid JSON in {config_file}: {e}[/red]")
        sys.exit(1)
    except Exception as e:
        print(f"[red][ERROR] Failed to read {config_file}: {e}[/red]")
        sys.exit(1)
    
    # Validate required keys
    required_keys = ['instance_url', 'api_token']
    missing_keys = [key for key in required_keys if key not in config]
    
    if missing_keys:
        print(f"[red][ERROR] Missing required keys in {config_file}: {', '.join(missing_keys)}[/red]")
        sys.exit(1)
    
    return config['instance_url'], config['api_token']

# Load configuration on startup
URL_PREFIX, API_TOKEN = load_config()

session = requests.Session()
session.headers.update({
    "Content-Type": "application/json",
    "Accept": "application/hal+json",
    "api-token": API_TOKEN
})

endpoint = f"{URL_PREFIX}api/v2/issue-tracker-profiles/"

REQUIRED_KEYS = [
    "issueTrackerType",
    "name",
    "userAsReporter",
    "url",
    "authenticationMethod",
    "username",
    "projectId",
    "proxyUrl",
    "proxyUsername",
    "issueLinkType"
]

def get_ids():
    """
    Gets the issue tracker profile ids, appends them to a dictionary, 
    and returns the total number of issue trackers.
    """
    profiles = []
    page = 0
    total_pages = 1 # Initialize with 1 to enter the loop

    print("[magenta]==>[/magenta] [bold]Finding issue trackers...[/bold]")

    while page < total_pages:
        try:
            response = session.get(
                endpoint,
                timeout=30,
                params={'page': page, 'size': 20}
            )
            response.raise_for_status()
            data = response.json()

            items = data.get("_embedded", {}).get("items", [])
            profiles.extend(item.get("id") for item in items if "id" in item)

            # Extract pagination info from the root of the response
            page_info = data.get("page", {}) 
            total_pages = page_info.get("totalPages", 1)
            
            # Increment page for the next iteration
            page += 1

        except Exception as e:
            print(f"[red]Error fetching page {page}: {e}[/red]")
            break

    print(f"Found {len(profiles)} total issue trackers.")
    return profiles

def fetch_all_tracker_configs(id_data):
    """
    Fetches all PUBLISHED tracker configurations without filtering or modification.
    Used for export-only operations where we need complete backups of current state.
    Only fetches published configs since those represent the current active state.
    
    Args:
        id_data: List of issue tracker IDs
    
    Returns:
        Tuple of (profile_data dict, unique_tracker_ids set)
    """
    profile_data = {}
    
    print("[magenta]==>[/magenta] [bold]Fetching all published issue tracker configurations...[/bold]")
    for ids in id_data:
        try:
            response = session.get(
                endpoint+ids,
                timeout=30
            )
            response.raise_for_status()
            data = response.json()
            published = data.get('published')
            
            # Only store published configuration (represents current active state)
            if published:
                config_key = f"{ids} (published)"
                profile_data[config_key] = (ids, published)
        except Exception as e:
            print(f"[yellow]Warning: Could not fetch config for {ids}: {e}[/yellow]")
            continue
    
    # Deduplicate tracker IDs
    unique_tracker_ids = set(tracker_id for tracker_id, _ in profile_data.values())
    print(f"Fetched published configurations for {len(unique_tracker_ids)} tracker(s)")
    return profile_data, unique_tracker_ids


def normalize_url(url):
    """
    Normalizes a URL by ensuring it has a scheme and converting to lowercase.
    If the URL is missing https://, it will be added.
    
    Args:
        url: URL string that may or may not have a scheme
    
    Returns:
        Lowercase URL string with https:// scheme guaranteed
    """
    if not url:
        return url
    
    # Check if URL already has a scheme (http://, https://, etc.)
    if "://" not in url:
        url = f"https://{url}"
    
    # Return lowercase URL for consistency
    return url.lower()

def get_issue_tracker_settings(id_data, new_url=None, update_url=False, update_creds=False, new_username=None, new_password=None, debug=False):
    """
    Gets the issue tracker settings parameters for each issue tracker id.
    Modifies data based on update flags.
    
    Processes both published and draft configurations for each tracker.
    Only processes Jira issue trackers.
    
    Args:
        id_data: List of issue tracker IDs
        new_url: New URL for URL updates (required if update_url is True)
        update_url: Whether to update URLs
        update_creds: Whether to update credentials (username-password auth only)
        new_username: New username for credentials update
        new_password: New password for credentials update
    """

    profile_data = {}
    skip_trackers = []
    needs_update_trackers = []
    unsupported_auth_trackers = []
    non_jira_trackers = []

    print("[magenta]==>[/magenta] [bold]Getting issue tracker data...[/bold]")
    for ids in id_data:
        response = session.get(
            endpoint+ids,
            timeout=30
            )
        data = response.json()
        published = data.get('published')
        draft = data.get('draft')
        
        # Validate it's a Jira issue tracker (check published since all trackers have it)
        if published and published.get('issueTrackerType') != 'jira':
            non_jira_trackers.append((ids, published.get('issueTrackerType')))
            continue
        
        # Only process draft configuration for updates
        # (When editing a published config via API, it automatically creates a draft)
        config = draft if draft else published
        
        if not config:
            continue
        
        # Create a key for this config (we track it as draft since that's what we update)
        config_key = f"{ids} (draft)"
        profile_data[config_key] = (ids, config)
        
        # Track whether this config needs any updates
        config_needs_update = False
        
        if update_url:
            current_url = config.get('url')
            config.update(url=new_url)
            if current_url != new_url:
                config_needs_update = True
                if debug:
                    print(f"    {config_key}: URL needs update ({current_url} → {new_url})")
            elif debug:
                print(f"    {config_key}: URL already correct ({current_url})")
        
        if update_creds:
            # Check if tracker uses username-password authentication
            auth_method = config.get('authenticationMethod')
            if auth_method == "username-password":
                # Capture original values BEFORE modifying
                original_username = config.get('username')
                original_password = config.get('password')
                
                if new_username:
                    config.update(username=new_username)
                if new_password:
                    config.update(password=new_password)
                
                # Check if tracker needs updating based on what we're changing
                if new_username and original_username != new_username:
                    config_needs_update = True
                    if debug:
                        print(f"    {config_key}: username needs update ({original_username} → {new_username})")
                elif new_username and debug:
                    print(f"    {config_key}: username already correct ({original_username})")
                
                if new_password and original_password != new_password:
                    config_needs_update = True
                    if debug:
                        print(f"    {config_key}: password needs update ({original_password} → {new_password})")
                elif new_password and debug:
                    print(f"    {config_key}: password already correct ({original_password})")
            else:
                # Tracker uses token auth or other method - skip for creds updates
                unsupported_auth_trackers.append((config_key, auth_method))
                if debug:
                    print(f"    {config_key}: skipped (auth method: {auth_method})")
        
        # Add to tracking lists based on whether this config needs updates
        if config_needs_update:
            if config_key not in needs_update_trackers:
                needs_update_trackers.append(config_key)
        else:
            if config_key not in skip_trackers:
                skip_trackers.append(config_key)
    
    # Print status summary
    if non_jira_trackers:
        print(f"Found {len(non_jira_trackers)} non-Jira issue trackers (skipped):")
        for tracker_id, tracker_type in non_jira_trackers:
            print(f"  - {tracker_id}: type '{tracker_type}'")
    
    # Build summary message based on what operations are being performed
    if update_url or update_creds:
        update_types = []
        if update_url:
            update_types.append("URL")
        if update_creds:
            update_types.append("credentials")
        update_label = " and ".join(update_types)
        
        # Count published vs draft configs in needs_update_trackers
        published_count = sum(1 for config_key in needs_update_trackers if " (published)" in config_key)
        draft_count = sum(1 for config_key in needs_update_trackers if " (draft)" in config_key)
        
        # Build summary message
        print(f"Found {len(skip_trackers)} issue tracker(s) with no changes needed and {len(needs_update_trackers)} that need {update_label} updating.")
    
    if update_creds:
        print(f"Found {len(unsupported_auth_trackers)} tracker config(s) with non-username/password authentication (skipped).")
        if unsupported_auth_trackers:
            for config_key, auth_method in unsupported_auth_trackers:
                print(f"  - {config_key}: uses '{auth_method}' authentication")

    if len(needs_update_trackers) == 0:
        print("[magenta]==>[/magenta] [bold]No issue trackers to update! Exiting.[/bold]")
        session.close()
        sys.exit()
    
    # Deduplicate tracker IDs from configs that need updating
    unique_tracker_ids = set(tracker_id for config_key in needs_update_trackers 
                            for tracker_id, _ in [profile_data[config_key]])
    return profile_data, needs_update_trackers, unique_tracker_ids

def update_issue_tracker(issue_tracker_data, needs_update_config_keys, operation="url"):
    """
    Performs a PUT request against the issue-tracker-profiles endpoint.
    Handles both URL and credentials updates.

    example minimum viable JSON payload to this endpoint:

    {
        "issueTrackerType": "jira",
        "name": "PROJECT : faeba2ec-93b8-4151-8a9c-4b5cbfb5fbee",
        "userAsReporter": false,
        "url": "https://iriusrisk.atlassian.net//",
        "authenticationMethod": "username-password",
        "username": "jkatz@iriusrisk.com",
        "projectId": "JKTZ",
        "proxyUrl": "",
        "proxyUsername": "",
        "issueLinkType": "Relates"
    }
    """

    confirmation = Prompt.ask(
        f"[magenta]==>[/magenta] [bold]Proceed to update {len(needs_update_config_keys)} issue tracker(s) ({operation})[/bold]",
        choices=["y", "yes", "n", "no"]
    )
    if confirmation.upper() in ["Y", "YES"]:
        for config_key, config_data in issue_tracker_data.items():
            issue_tracker_id, tracker = config_data
            final_payload = {
                    key: tracker.get(key)
                    for key in REQUIRED_KEYS
                    if key in tracker
            }
            response = session.put(
                endpoint+issue_tracker_id,
                data=json.dumps(final_payload),
                timeout=30
                )
            if response.status_code == 200:
                print(f"Issue tracker ({config_key}) successfully updated!")
            elif response.status_code == 400:
                print(f"[yellow]Issue tracker ({config_key}): Bad request - Invalid data[/yellow]")
                print(f"  Details: {response.text}")
            elif response.status_code == 401:
                print(f"[red]Issue tracker ({config_key}): Authentication failed - Invalid API token[/red]")
                sys.exit(1)
            elif response.status_code == 403:
                print(f"[red]Issue tracker ({config_key}): Permission denied - Insufficient access[/red]")
            elif response.status_code == 404:
                print(f"[red]Issue tracker ({config_key}): Not found - Tracker may have been deleted[/red]")
            elif response.status_code >= 500:
                print(f"[red]Issue tracker ({config_key}): Server error (HTTP {response.status_code})[/red]")
                print(f"  Details: {response.text}")
            else:
                print(f"[red]Issue tracker ({config_key}): Unexpected error (HTTP {response.status_code})[/red]")
                print(f"  Details: {response.text}")
    elif confirmation.upper() in ["N", "NO"]:
        print("Stopping program")
        sys.exit()
    else:
        print("Invalid input")

def export_trackers(issue_tracker_data, unique_tracker_ids):
    """
    Exports current issue tracker configurations to a backup JSON file.
    Useful for rollback if updates fail or for auditing.
    
    Args:
        issue_tracker_data: Dictionary of tracker configurations
        unique_tracker_ids: Set of unique tracker IDs
    
    Returns:
        Path to the exported backup file
    """
    from datetime import datetime
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_filename = f"tracker_backup_{timestamp}.json"
    
    # Prepare backup data with metadata
    backup_data = {
        "exported_at": datetime.now().isoformat(),
        "tracker_count": len(unique_tracker_ids),
        "configs": {}
    }
    
    # Store configs in a clean format
    for config_key, (tracker_id, config) in issue_tracker_data.items():
        backup_data["configs"][config_key] = config
    
    # Write to file
    try:
        with open(backup_filename, 'w') as f:
            json.dump(backup_data, f, indent=2, default=str)
        print(f"[bold green]✓ Configuration backup saved to {backup_filename}[/bold green]")
        return backup_filename
    except Exception as e:
        print(f"[bold red][WARNING][/bold red] Failed to export backup: {e}")
        return None

def publish_trackers(unique_tracker_ids):
    """
    Publishes draft configurations to live for each tracker.
    
    Args:
        unique_tracker_ids: Set of unique tracker IDs to publish
    """
    print("[magenta]==>[/magenta] [bold]Publishing changes...[/bold]")
    
    for tracker_id in unique_tracker_ids:
        try:
            response = session.post(
                f"{endpoint}{tracker_id}/publish",
                timeout=30
            )
            if response.status_code == 200:
                print(f"[bold green]  ✓[/bold green] {tracker_id}: Published successfully")
            elif response.status_code == 404:
                print(f"[bold red]  ✗[/bold red] {tracker_id}: Not found - may have been deleted")
            elif response.status_code == 400:
                print(f"[bold red]  ✗[/bold red] {tracker_id}: Cannot publish - invalid configuration")
            else:
                print(f"[bold red]  ✗[/bold red] {tracker_id}: Publish failed (HTTP {response.status_code})")
        except Exception as e:
            print(f"[bold red]  ✗[/bold red] {tracker_id}: Error during publish - {e}")

def validate_trackers(unique_tracker_ids):
    """
    Tests the connection and credentials for each updated issue tracker.
    
    Args:
        unique_tracker_ids: Set of tracker IDs to validate
    
    Returns:
        Tuple of (valid_trackers, invalid_trackers)
    """
    valid_trackers = []
    invalid_trackers = []
    
    print("[magenta]==>[/magenta] [bold]Validating issue tracker credentials...[/bold]")
    
    for tracker_id in unique_tracker_ids:
        try:
            response = session.post(
                f"{endpoint}{tracker_id}/test",
                timeout=30
            )
            if response.status_code == 200:
                valid_trackers.append(tracker_id)
                print(f"[bold green]  ✓[/bold green] {tracker_id}: Connection successful")
            else:
                invalid_trackers.append(tracker_id)
                print(f"[bold red]  ✗[/bold red] {tracker_id}: Connection failed (HTTP {response.status_code})")
        except Exception as e:
            invalid_trackers.append(tracker_id)
            print(f"[bold red]  ✗[/bold red] {tracker_id}: Connection error - {e}")
    
    print(f"\nValidation Summary: {len(valid_trackers)} successful, {len(invalid_trackers)} failed")
    return valid_trackers, invalid_trackers

def main():
    """
    Executes all main functions of the program.
    Supports URL and credentials updates via argparse flags.
    """
    parser = argparse.ArgumentParser(
        description="Update Jira issue tracker profiles in IriusRisk"
    )
    parser.add_argument(
        "--url",
        type=str,
        help="Update issue tracker URLs to the specified URL"
    )
    parser.add_argument(
        "--username",
        type=str,
        help="Update issue tracker username (username-password auth only)"
    )
    parser.add_argument(
        "--password",
        type=str,
        help="Update issue tracker password (username-password auth only)"
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug output"
    )
    parser.add_argument(
        "--validate",
        action="store_true",
        help="Validate tracker credentials after updating"
    )
    parser.add_argument(
        "--export",
        action="store_true",
        help="Export current configurations to backup file before updating"
    )
    args = parser.parse_args()
    
    # Validate that at least one operation was specified
    if not args.url and not args.username and not args.password and not args.export:
        print("[red][ERROR] Please specify --url and/or --username and/or --password and/or --export[/red]")
        parser.print_help()
        sys.exit(1)
    
    try:
        issue_tracker_ids = get_ids()
        
        # Determine what updates to perform
        update_url = args.url is not None
        update_creds = args.username is not None or args.password is not None
        new_username = args.username
        new_password = args.password
        
        # Normalize URL if provided (ensure it has https:// scheme and is lowercase)
        normalized_url = normalize_url(args.url) if args.url else None
        
        # Display mode info
        if update_url:
            print("\n[bold blue]=== URL UPDATE MODE ===[/bold blue]")
            print(f"  New URL: {normalized_url}")
        if update_creds:
            print("\n[bold blue]=== CREDENTIALS UPDATE MODE ===[/bold blue]")
            if args.username:
                print(f"  Username: {args.username}")
            if args.password:
                print(f"  Password: {'*' * len(args.password)}")
        
        # Only fetch and process settings if updates are requested
        if update_url or update_creds:
            issue_tracker_settings, needs_update_trackers, unique_tracker_ids = get_issue_tracker_settings(
                issue_tracker_ids,
                new_url=normalized_url,
                update_url=update_url,
                update_creds=update_creds,
                new_username=new_username,
                new_password=new_password,
                debug=args.debug
            )
        else:
            # Export-only mode: fetch all configs for complete backup
            issue_tracker_settings, unique_tracker_ids = fetch_all_tracker_configs(issue_tracker_ids)
            needs_update_trackers = None  # Not used in export-only mode
        
        # Export backup if requested
        if args.export:
            export_trackers(issue_tracker_settings, unique_tracker_ids)
        
        # Only proceed with updates if URL or credentials were specified
        if update_url or update_creds:
            # Update with appropriate label
            labels = []
            if update_url:
                labels.append("URLs")
            if args.username:
                labels.append("username")
            if args.password:
                labels.append("password")
            operation = " and ".join(labels)
                
            update_issue_tracker(issue_tracker_settings, needs_update_trackers, operation=operation)
            
            # Publish changes after successful update
            publish_trackers(unique_tracker_ids)
            
            # Validate the updated trackers if requested
            if args.validate:
                valid_trackers, invalid_trackers = validate_trackers(unique_tracker_ids)
                if invalid_trackers:
                    print(f"\n[yellow][WARNING] {len(invalid_trackers)} tracker(s) failed validation. Please verify credentials.[/yellow]")
                else:
                    print(f"\n[bold green][SUCCESS][/green] All {len(valid_trackers)} tracker(s) validated successfully![/bold green]")
            else:
                print(f"\n[bold green][SUCCESS] Updated {len(unique_tracker_ids)} tracker(s) successfully![/bold green]")
                print("[dim]Tip: Use --validate flag to test credentials after updating[/dim]")
        elif args.export:
            print(f"\n[bold green][SUCCESS] Exported backup successfully![/bold green]")
        
        session.close()
        
    except Exception as error:
        print(f"[bold red][ERROR] Issue tracker updating failed.\n Reason: {error}[/bold red]")
        session.close()
        sys.exit(1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n[yellow]Operation cancelled by user[/yellow]")
        sys.exit(0)




import requests
import json
import os
import argparse
from tabulate import tabulate
import csv
import re
import logging
from typing import List, Dict, Optional, Any, Generator
from datetime import datetime
import time
from colorama import init, Fore, Style
import pandas as pd

# Initialize colorama
init()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(f'okta_group_lister_{datetime.now().strftime("%Y%m%d")}.log')
    ]
)
logger = logging.getLogger(__name__)

OKTA_DOMAIN = os.environ.get("OKTA_DOMAIN")
API_TOKEN = os.environ.get("OKTA_API_TOKEN")
MAX_RETRIES = 3
RETRY_DELAY = 1  # seconds
RATE_LIMIT_DELAY = 1  # seconds

class OktaAPIError(Exception):
    """Custom exception for Okta API errors."""
    pass

def handle_rate_limit(response: requests.Response) -> None:
    """Handle rate limiting by checking response headers and waiting if necessary."""
    if 'X-Rate-Limit-Remaining' in response.headers:
        remaining = int(response.headers['X-Rate-Limit-Remaining'])
        if remaining < 10:  # If we're close to the limit
            reset_time = int(response.headers.get('X-Rate-Limit-Reset', 0))
            if reset_time > 0:
                wait_time = reset_time - int(time.time())
                if wait_time > 0:
                    logger.warning(f"Rate limit nearly reached. Waiting {wait_time} seconds...")
                    time.sleep(wait_time)
            else:
                logger.warning("Rate limit nearly reached. Waiting default delay...")
                time.sleep(RATE_LIMIT_DELAY)

def make_api_request(url: str, headers: Dict[str, str], params: Optional[Dict[str, Any]] = None) -> requests.Response:
    """Make an API request with retry logic and rate limit handling."""
    for attempt in range(MAX_RETRIES):
        try:
            response = requests.get(url, headers=headers, params=params)
            handle_rate_limit(response)
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            if attempt == MAX_RETRIES - 1:
                raise
            logger.warning(f"Request failed (attempt {attempt + 1}/{MAX_RETRIES}): {e}")
            time.sleep(RETRY_DELAY * (attempt + 1))  # Exponential backoff

def fetch_groups(search_term: Optional[str] = None) -> Optional[List[Dict[str, Any]]]:
    """Fetches groups from the Okta API with pagination support.
    Args:
        search_term: Optional string to search for in group names (case-insensitive).
    Returns:
        A list of group dictionaries, or None on error.
    Raises:
        OktaAPIError: If there's an error with the API call.
    """
    if not OKTA_DOMAIN or not API_TOKEN:
        logger.error("OKTA_DOMAIN and OKTA_API_TOKEN environment variables must be set.")
        raise OktaAPIError("Missing required environment variables")

    headers = {
        "Authorization": f"SSWS {API_TOKEN}",
        "Content-Type": "application/json",
    }
    base_url = f"https://{OKTA_DOMAIN}/api/v1/groups"
    all_groups = []
    limit = 100  # Maximum number of results per page
    after = None

    try:
        while True:
            params = {"limit": limit}
            if after:
                params["after"] = after

            logger.info(f"Fetching groups page from Okta API{f' with search term: {search_term}' if search_term else ''}")
            response = make_api_request(base_url, headers, params)
            groups_data = response.json()
            
            if not groups_data:
                break

            all_groups.extend(groups_data)
            
            # Check if there are more pages
            if len(groups_data) < limit:
                break
                
            # Get the last group's ID for pagination
            after = groups_data[-1]["id"]

        if search_term:
            search_term_lower = search_term.lower()
            filtered_groups = [
                group
                for group in all_groups
                if search_term_lower in group["profile"]["name"].lower()
            ]
            logger.info(f"Found {len(filtered_groups)} groups matching search term")
            return filtered_groups
        else:
            logger.info(f"Found {len(all_groups)} total groups")
            return all_groups

    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching groups: {e}")
        raise OktaAPIError(f"Failed to fetch groups: {str(e)}")
    except json.JSONDecodeError:
        logger.error("Error decoding JSON response from Okta API")
        raise OktaAPIError("Invalid JSON response from Okta API")

def display_groups(groups: List[Dict[str, Any]]) -> None:
    """Displays the list of groups in a formatted table with colors.
    Args:
        groups: A list of group dictionaries.
    """
    if not groups:
        print(f"{Fore.YELLOW}No groups found.{Style.RESET_ALL}")
        return

    headers = ["ID", "Name", "Description"]
    table_data = []
    for group in groups:
        description = group['profile'].get('description', '-')  # Default to "-" if missing
        table_data.append([
            f"{Fore.CYAN}{group['id']}{Style.RESET_ALL}",
            f"{Fore.GREEN}{group['profile']['name']}{Style.RESET_ALL}",
            description
        ])

    print(f"\n{Fore.BLUE}Groups:{Style.RESET_ALL}")
    print(tabulate(table_data, headers=headers, tablefmt="grid"))

def fetch_group_members(group_id: str) -> Optional[List[Dict[str, Any]]]:
    """Fetches the members of a specific Okta group with pagination support.
    Args:
        group_id: The ID of the group.
    Returns:
        A list of member dictionaries, or None on error.
    Raises:
        OktaAPIError: If there's an error with the API call.
    """
    if not OKTA_DOMAIN or not API_TOKEN:
        logger.error("OKTA_DOMAIN and OKTA_API_TOKEN environment variables must be set.")
        raise OktaAPIError("Missing required environment variables")

    headers = {
        "Authorization": f"SSWS {API_TOKEN}",
        "Content-Type": "application/json",
    }
    base_url = f"https://{OKTA_DOMAIN}/api/v1/groups/{group_id}/users"
    all_members = []
    limit = 100  # Maximum number of results per page
    after = None

    try:
        while True:
            params = {"limit": limit}
            if after:
                params["after"] = after

            logger.info(f"Fetching members page for group ID: {group_id}")
            response = make_api_request(base_url, headers, params)
            members_data = response.json()
            
            if not members_data:
                break

            all_members.extend(members_data)
            
            # Check if there are more pages
            if len(members_data) < limit:
                break
                
            # Get the last member's ID for pagination
            after = members_data[-1]["id"]

        logger.info(f"Found {len(all_members)} members in group")
        return all_members

    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching group members for group ID {group_id}: {e}")
        raise OktaAPIError(f"Failed to fetch group members: {str(e)}")
    except json.JSONDecodeError:
        logger.error("Error decoding JSON response from Okta API")
        raise OktaAPIError("Invalid JSON response from Okta API")

def display_group_members(members: List[Dict[str, Any]]) -> None:
    """Displays the members of a group in a formatted table with colors.
    Args:
        members: A list of member dictionaries.
    """
    if not members:
        print(f"{Fore.YELLOW}No members found in the specified group.{Style.RESET_ALL}")
        return

    headers = ["ID", "Login", "Email", "Name"]
    table_data = []
    for member in members:
        user_id = member["id"]
        login = member["profile"].get("login", "-")
        email = member["profile"].get("email", "-")
        first_name = member["profile"].get("firstName", "-")
        last_name = member["profile"].get("lastName", "-")
        full_name = f"{first_name} {last_name}".strip() or "-"
        table_data.append([
            f"{Fore.CYAN}{user_id}{Style.RESET_ALL}",
            f"{Fore.GREEN}{login}{Style.RESET_ALL}",
            email,
            full_name
        ])

    print(f"\n{Fore.BLUE}Group Members:{Style.RESET_ALL}")
    print(tabulate(table_data, headers=headers, tablefmt="grid"))

def export_group_members(members: List[Dict[str, Any]], group_name: str, format: str = "csv") -> None:
    """Exports the members of a group to a file in the specified format.
    Args:
        members: A list of member dictionaries.
        group_name: The name of the group (used for the filename).
        format: The export format ("csv" or "json").
    """
    if not members:
        logger.warning("No members to export.")
        return

    sanitized_group_name = re.sub(r"[^a-zA-Z0-9_.-]", "_", group_name)
    base_filename = os.path.join(os.path.expanduser("~"), f"{sanitized_group_name}_members")

    try:
        if format.lower() == "json":
            filename = f"{base_filename}.json"
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(members, f, indent=2)
        elif format.lower() == "excel":
            filename = f"{base_filename}.xlsx"
            df = pd.DataFrame([
                {
                    "ID": member["id"],
                    "Login": member["profile"].get("login", "-"),
                    "Email": member["profile"].get("email", "-"),
                    "FirstName": member["profile"].get("firstName", "-"),
                    "LastName": member["profile"].get("lastName", "-"),
                }
                for member in members
            ])
            df.to_excel(filename, index=False)
        else:  # CSV format
            filename = f"{base_filename}.csv"
            fieldnames = ["ID", "Login", "Email", "FirstName", "LastName"]
            with open(filename, "w", newline="", encoding="utf-8") as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                for member in members:
                    writer.writerow({
                        "ID": member["id"],
                        "Login": member["profile"].get("login", "-"),
                        "Email": member["profile"].get("email", "-"),
                        "FirstName": member["profile"].get("firstName", "-"),
                        "LastName": member["profile"].get("lastName", "-"),
                    })
        
        print(f"{Fore.GREEN}Successfully exported group members to: {filename}{Style.RESET_ALL}")
    except Exception as e:
        logger.error(f"Error exporting to {format}: {e}")
        print(f"{Fore.RED}Error exporting to {format}: {e}. Check file path and permissions.{Style.RESET_ALL}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="List and manage Okta groups and their members.")
    parser.add_argument("--search", help="Search for groups by name (case-insensitive substring match).")
    parser.add_argument(
        "--members",
        help="List members of the group with this name or ID. If a name matches multiple groups, you must use the ID.",
    )
    parser.add_argument(
        "--export",
        help="Export members of the group with this name or ID. If a name matches multiple groups, you must use the ID."
    )
    parser.add_argument(
        "--format",
        choices=["csv", "json", "excel"],
        default="csv",
        help="Export format (default: csv)"
    )
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
    args = parser.parse_args()

    if args.verbose:
        logger.setLevel(logging.DEBUG)

    try:
        if args.export:
            group_identifier = args.export
            try:
                members = fetch_group_members(group_identifier)  # try it as an ID first
                if members is not None:  # if it is an ID
                    group_data = fetch_groups(search_term=group_identifier)
                    if group_data and len(group_data) == 1:
                        export_group_members(members, group_data[0]['profile']['name'], args.format)
                    else:
                        logger.warning(f"Could not find group name for ID '{group_identifier}'.")
                        export_group_members(members, group_identifier, args.format)
                else:
                    groups = fetch_groups(search_term=group_identifier)
                    if groups:
                        if len(groups) == 1:
                            group_id = groups[0]["id"]
                            members = fetch_group_members(group_id)
                            if members:
                                export_group_members(members, groups[0]['profile']['name'], args.format)
                            else:
                                logger.error(f"Could not fetch members for group '{group_identifier}'.")
                        elif len(groups) > 1:
                            logger.warning(f"Multiple groups found with the name '{group_identifier}'.")
                            for group in groups:
                                print(f"  ID: {group['id']}, Name: {group['profile']['name']}")
                        else:
                            logger.error(f"No group found with the name '{group_identifier}'.")
                    else:
                        logger.error(f"Error fetching groups matching '{group_identifier}'.")
            except OktaAPIError as e:
                logger.error(f"API Error: {e}")
                exit(1)

        elif args.members:
            group_identifier = args.members
            try:
                members = fetch_group_members(group_identifier)
                if members is not None:
                    display_group_members(members)
                else:
                    groups = fetch_groups(search_term=group_identifier)
                    if groups:
                        if len(groups) == 1:
                            group_id = groups[0]["id"]
                            members = fetch_group_members(group_id)
                            display_group_members(members)
                        elif len(groups) > 1:
                            logger.warning(f"Multiple groups found with the name '{group_identifier}'.")
                            for group in groups:
                                print(f"  ID: {group['id']}, Name: {group['profile']['name']}")
                        else:
                            logger.error(f"No group found with the name '{group_identifier}'.")
                    else:
                        logger.error(f"Error fetching groups matching '{group_identifier}'.")
            except OktaAPIError as e:
                logger.error(f"API Error: {e}")
                exit(1)

        elif args.search:
            search_term = args.search
            try:
                groups = fetch_groups(search_term=search_term)
                display_groups(groups)
            except OktaAPIError as e:
                logger.error(f"API Error: {e}")
                exit(1)

        else:
            try:
                groups = fetch_groups()
                display_groups(groups)
            except OktaAPIError as e:
                logger.error(f"API Error: {e}")
                exit(1)

    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        exit(1)

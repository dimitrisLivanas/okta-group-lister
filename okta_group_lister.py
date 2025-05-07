import requests
import json
import os
import argparse
from tabulate import tabulate
import csv
import re  # Import the regular expression module


OKTA_DOMAIN = os.environ.get("OKTA_DOMAIN")
API_TOKEN = os.environ.get("OKTA_API_TOKEN")

def fetch_groups(search_term=None):
    """Fetches groups from the Okta API.
    Args:
        search_term: Optional string to search for in group names (case-insensitive).
    Returns:
        A list of group dictionaries, or None on error.
    """
    if not OKTA_DOMAIN or not API_TOKEN:
        print("Error: OKTA_DOMAIN and OKTA_API_TOKEN environment variables must be set.")
        return None

    headers = {
        "Authorization": f"SSWS {API_TOKEN}",
        "Content-Type": "application/json",
    }
    url = f"https://{OKTA_DOMAIN}/api/v1/groups"
    params = {}

    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()  # Raise HTTPError for bad responses
        groups_data = response.json()

        if search_term:
            search_term_lower = search_term.lower()
            filtered_groups = [
                group
                for group in groups_data
                if search_term_lower in group["profile"]["name"].lower()
            ]
            return filtered_groups
        else:
            return groups_data

    except requests.exceptions.RequestException as e:
        print(f"Error fetching groups: {e}")
        return None
    except json.JSONDecodeError:
        print("Error decoding JSON response.")
        return None



def display_groups(groups):
    """Displays the list of groups in a formatted table.
    Args:
        groups: A list of group dictionaries.
    """
    if not groups:
        print("No groups found.")
        return

    headers = ["ID", "Name", "Description"]
    table_data = []
    for group in groups:
        description = group['profile'].get('description', '-')  # Default to "-" if missing
        table_data.append([group['id'], group['profile']['name'], description])

    print(tabulate(table_data, headers=headers, tablefmt="grid"))  # Use grid for better formatting



def fetch_group_members(group_id):
    """Fetches the members of a specific Okta group.
    Args:
        group_id: The ID of the group.
    Returns:
        A list of member dictionaries, or None on error.
    """
    if not OKTA_DOMAIN or not API_TOKEN:
        print("Error: OKTA_DOMAIN and OKTA_API_TOKEN environment variables must be set.")
        return None

    headers = {
        "Authorization": f"SSWS {API_TOKEN}",
        "Content-Type": "application/json",
    }
    url = f"https://{OKTA_DOMAIN}/api/v1/groups/{group_id}/users"

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        members_data = response.json()
        return members_data
    except requests.exceptions.RequestException as e:
        print(f"Error fetching group members for group ID {group_id}: {e}")
        return None
    except json.JSONDecodeError:
        print("Error decoding JSON response.")
        return None



def display_group_members(members):
    """Displays the members of a group in a formatted table.
    Args:
        members: A list of member dictionaries.
    """
    if not members:
        print("No members found in the specified group.")
        return

    headers = ["ID", "Login", "Email", "Name"]
    table_data = []
    for member in members:
        user_id = member["id"]
        login = member["profile"].get("login", "-")
        email = member["profile"].get("email", "-")
        first_name = member["profile"].get("firstName", "-")
        last_name = member["profile"].get("lastName", "-")
        full_name = f"{first_name} {last_name}".strip() or "-"  # Handle missing names
        table_data.append([user_id, login, email, full_name])

    print(tabulate(table_data, headers=headers, tablefmt="grid"))  # Use grid for better formatting



def export_group_members_to_csv(members, group_name):
    """Exports the members of a group to a CSV file in the user's home directory.
    Args:
        members: A list of member dictionaries.
        group_name: The name of the group (used for the filename).
    """
    if not members:
        print("No members to export.")
        return

    fieldnames = ["ID", "Login", "Email", "FirstName", "LastName"]
    sanitized_group_name = re.sub(r"[^a-zA-Z0-9_.-]", "_", group_name)
    filename = os.path.join(os.path.expanduser("~"), f"{sanitized_group_name}_members.csv")

    try:
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
        print(f"Successfully exported group members to: {filename}")
    except Exception as e:
        print(f"Error exporting to CSV: {e}.  Check file path and permissions.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="List and manage Okta groups and their members.")
    parser.add_argument("--search", help="Search for groups by name (case-insensitive substring match).")
    parser.add_argument(
        "--members",
        help="List members of the group with this name or ID.  If a name matches multiple groups, you must use the ID.",
    )
    parser.add_argument("--export", help="Export members of the group with this name or ID.  If a name matches multiple groups, you must use the ID.")
    args = parser.parse_args()

    if args.export:
        group_identifier = args.export
        members = fetch_group_members(group_identifier) # try it as an ID first
        if members is not None: # if it is an ID
            #  Need to fetch group name to use in export
            group_data = fetch_groups(search_term=group_identifier)
            if group_data:
                if len(group_data) == 1:
                  export_group_members_to_csv(members, group_data[0]['profile']['name'])
                else:
                  print(f"Could not find group name for  ID '{group_identifier}'.")
                  export_group_members_to_csv(members, group_identifier) # export with ID as name
            else:
                export_group_members_to_csv(members, group_identifier) # export with ID as name
        else:
            groups = fetch_groups(search_term=group_identifier)  # Find the group by name
            if groups:
                if len(groups) == 1:
                    group_id = groups[0]["id"]
                    members = fetch_group_members(group_id)
                    if members:
                        export_group_members_to_csv(members, groups[0]['profile']['name'])
                    else:
                        print(f"Could not fetch members for group '{group_identifier}'.")
                elif len(groups) > 1:
                    print(
                        f"Multiple groups found with the name '{group_identifier}'.  Use the Group ID (from the following list) with --export."
                    )
                    for group in groups:
                        print(f"  ID: {group['id']}, Name: {group['profile']['name']}")
                else:
                    print(f"No group found with the name '{group_identifier}'.")
            else:
                print(f"Error fetching groups matching '{group_identifier}'.")



    elif args.members:
        group_identifier = args.members  # Could be name or ID
        members = fetch_group_members(group_identifier) # try it as an ID first
        if members is not None:
            display_group_members(members)
        else:
            # If that didn't work, try to treat it as a name.
            groups = fetch_groups(search_term=group_identifier)
            if groups:
                if len(groups) == 1:
                    group_id = groups[0]["id"]
                    members = fetch_group_members(group_id)
                    display_group_members(members)
                elif len(groups) > 1:
                    print(
                        f"Multiple groups found with the name '{group_identifier}'.  Use the Group ID (from the following list) with --members."
                    )
                    for group in groups:
                        print(f"  ID: {group['id']}, Name: {group['profile']['name']}")
                else:
                    print(f"No group found with the name '{group_identifier}'.")
            else:
                print(f"Error fetching groups matching '{group_identifier}'.")  # more general


    elif args.search:
        search_term = args.search
        groups = fetch_groups(search_term=search_term)
        display_groups(groups)

    else:
        groups = fetch_groups()
        display_groups(groups)

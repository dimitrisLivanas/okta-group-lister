import requests
import json
import os
from tabulate import tabulate

OKTA_DOMAIN = os.environ.get("OKTA_DOMAIN")
API_TOKEN = os.environ.get("OKTA_API_TOKEN")

def fetch_okta_groups():
    """Fetches the list of groups from the Okta API."""
    if not OKTA_DOMAIN or not API_TOKEN:
        print("Error: OKTA_DOMAIN and OKTA_API_TOKEN environment variables must be set.")
        return None

    headers = {
        "Authorization": f"SSWS {API_TOKEN}",
        "Content-Type": "application/json"
    }
    url = f"https://{OKTA_DOMAIN}/api/v1/groups"

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching groups: {e}")
        return None
    except json.JSONDecodeError:
        print("Error decoding JSON response.")
        return None

def display_groups(groups):
    """Displays the list of groups in a formatted table."""
    if not groups:
        print("No groups found.")
        return

    headers = ["ID", "Name", "Description"]
    table_data = []
    for group in groups:
        description = group['profile'].get('description', '-')
        table_data.append([group['id'], group['profile']['name'], description])

    print(tabulate(table_data, headers=headers, tablefmt="grid"))

if __name__ == "__main__":
    groups = fetch_okta_groups()
    if groups:
        display_groups(groups)
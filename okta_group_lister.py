import os
import argparse
import logging
from datetime import datetime
from colorama import init
from okta_group_lister import OktaClient, OktaAPIError, get_exporter

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

def main():
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

    if not os.environ.get("OKTA_DOMAIN") or not os.environ.get("OKTA_API_TOKEN"):
        logger.error("OKTA_DOMAIN and OKTA_API_TOKEN environment variables must be set.")
        exit(1)

    client = OktaClient(os.environ["OKTA_DOMAIN"], os.environ["OKTA_API_TOKEN"])

    try:
        if args.export:
            group_identifier = args.export
            try:
                members = client.fetch_group_members(group_identifier)
                if members:
                    groups = client.fetch_groups(search_term=group_identifier)
                    if groups and len(groups) == 1:
                        group_name = groups[0].name
                    else:
                        group_name = group_identifier
                    exporter = get_exporter(args.format, members, group_name)
                    exporter.export()
                else:
                    groups = client.fetch_groups(search_term=group_identifier)
                    if groups:
                        if len(groups) == 1:
                            members = client.fetch_group_members(groups[0].id)
                            if members:
                                exporter = get_exporter(args.format, members, groups[0].name)
                                exporter.export()
                            else:
                                logger.error(f"Could not fetch members for group '{group_identifier}'.")
                        elif len(groups) > 1:
                            logger.warning(f"Multiple groups found with the name '{group_identifier}'.")
                            for group in groups:
                                print(f"  ID: {group.id}, Name: {group.name}")
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
                members = client.fetch_group_members(group_identifier)
                if members:
                    for member in members:
                        member.display()
                else:
                    groups = client.fetch_groups(search_term=group_identifier)
                    if groups:
                        if len(groups) == 1:
                            members = client.fetch_group_members(groups[0].id)
                            for member in members:
                                member.display()
                        elif len(groups) > 1:
                            logger.warning(f"Multiple groups found with the name '{group_identifier}'.")
                            for group in groups:
                                print(f"  ID: {group.id}, Name: {group.name}")
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
                groups = client.fetch_groups(search_term=search_term)
                for group in groups:
                    group.display()
            except OktaAPIError as e:
                logger.error(f"API Error: {e}")
                exit(1)

        else:
            try:
                groups = client.fetch_groups()
                for group in groups:
                    group.display()
            except OktaAPIError as e:
                logger.error(f"API Error: {e}")
                exit(1)

    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        exit(1)

if __name__ == "__main__":
    main()

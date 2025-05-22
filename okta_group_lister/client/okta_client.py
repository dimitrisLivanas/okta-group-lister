import requests
import json
import logging
import time
from typing import List, Dict, Optional, Any
from ..models.group import Group
from ..models.member import Member

logger = logging.getLogger(__name__)

class OktaAPIError(Exception):
    """Custom exception for Okta API errors."""
    pass

class OktaClient:
    def __init__(self, domain: str, api_token: str):
        self.domain = domain
        self.api_token = api_token
        self.headers = {
            "Authorization": f"SSWS {api_token}",
            "Content-Type": "application/json",
        }
        self.max_retries = 3
        self.retry_delay = 1
        self.rate_limit_delay = 1

    def _handle_rate_limit(self, response: requests.Response) -> None:
        if 'X-Rate-Limit-Remaining' in response.headers:
            remaining = int(response.headers['X-Rate-Limit-Remaining'])
            if remaining < 10:
                reset_time = int(response.headers.get('X-Rate-Limit-Reset', 0))
                if reset_time > 0:
                    wait_time = reset_time - int(time.time())
                    if wait_time > 0:
                        logger.warning(f"Rate limit nearly reached. Waiting {wait_time} seconds...")
                        time.sleep(wait_time)
                else:
                    logger.warning("Rate limit nearly reached. Waiting default delay...")
                    time.sleep(self.rate_limit_delay)

    def _make_request(self, url: str, params: Optional[Dict[str, Any]] = None) -> requests.Response:
        for attempt in range(self.max_retries):
            try:
                response = requests.get(url, headers=self.headers, params=params)
                self._handle_rate_limit(response)
                response.raise_for_status()
                return response
            except requests.exceptions.RequestException as e:
                if attempt == self.max_retries - 1:
                    raise
                logger.warning(f"Request failed (attempt {attempt + 1}/{self.max_retries}): {e}")
                time.sleep(self.retry_delay * (attempt + 1))

    def fetch_groups(self, search_term: Optional[str] = None) -> List[Group]:
        base_url = f"https://{self.domain}/api/v1/groups"
        all_groups = []
        limit = 100
        after = None

        try:
            while True:
                params = {"limit": limit}
                if after:
                    params["after"] = after

                logger.info(f"Fetching groups page from Okta API{f' with search term: {search_term}' if search_term else ''}")
                response = self._make_request(base_url, params)
                groups_data = response.json()
                
                if not groups_data:
                    break

                all_groups.extend([Group.from_dict(group) for group in groups_data])
                
                if len(groups_data) < limit:
                    break
                    
                after = groups_data[-1]["id"]

            if search_term:
                search_term_lower = search_term.lower()
                filtered_groups = [
                    group for group in all_groups
                    if search_term_lower in group.name.lower()
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

    def fetch_group_members(self, group_id: str) -> List[Member]:
        base_url = f"https://{self.domain}/api/v1/groups/{group_id}/users"
        all_members = []
        limit = 100
        after = None

        try:
            while True:
                params = {"limit": limit}
                if after:
                    params["after"] = after

                logger.info(f"Fetching members page for group ID: {group_id}")
                response = self._make_request(base_url, params)
                members_data = response.json()
                
                if not members_data:
                    break

                all_members.extend([Member.from_dict(member) for member in members_data])
                
                if len(members_data) < limit:
                    break
                    
                after = members_data[-1]["id"]

            logger.info(f"Found {len(all_members)} members in group")
            return all_members

        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching group members for group ID {group_id}: {e}")
            raise OktaAPIError(f"Failed to fetch group members: {str(e)}")
        except json.JSONDecodeError:
            logger.error("Error decoding JSON response from Okta API")
            raise OktaAPIError("Invalid JSON response from Okta API") 
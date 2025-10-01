# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Authentication client for Kite integration."""

import json
import logging
from typing import Dict, Optional, Tuple
from datetime import datetime, timedelta
import requests

class KiteAuthClient:
    """Client for handling Kite authentication and agent configuration."""

    def __init__(self, auth_server_url: str = "http://localhost:8004"):
        self.auth_server_url = auth_server_url
        self.session = requests.Session()
        self._user_info = None
        self._agent_config = None

    def get_auth_url(self) -> str:
        """Get the authentication URL for Kite login."""
        return f"{self.auth_server_url}/auth/login"

    def get_auth_status(self) -> Tuple[bool, Optional[Dict]]:
        """Check if user is authenticated and get user info."""
        try:
            response = self.session.get(f"{self.auth_server_url}/auth/status")
            if response.status_code == 200:
                data = response.json()
                if data.get('authenticated'):
                    self._user_info = {
                        'username': data.get('username'),
                        'agent_id': data.get('agent_id'),
                        'agent_config': data.get('agent_config')
                    }
                    self._agent_config = data.get('agent_config')
                    return True, self._user_info
            return False, None
        except Exception as e:
            logging.error(f"Auth status check failed: {e}")
            return False, None

    def get_auth_status_with_cookies(self, cookies) -> Tuple[bool, Optional[Dict]]:
        """Check if user is authenticated with specific cookies."""
        try:
            # Create a new session for this request to avoid cookie conflicts
            import requests
            temp_session = requests.Session()

            # Forward the cookies from the shopping agent to the auth server
            response = temp_session.get(
                f"{self.auth_server_url}/auth/status",
                cookies=cookies
            )
            if response.status_code == 200:
                data = response.json()
                if data.get('authenticated'):
                    self._user_info = {
                        'username': data.get('username'),
                        'agent_id': data.get('agent_id'),
                        'agent_config': data.get('agent_config')
                    }
                    self._agent_config = data.get('agent_config')
                    return True, self._user_info
            return False, None
        except Exception as e:
            logging.error(f"Auth status check with cookies failed: {e}")
            return False, None

    def get_user_info(self) -> Optional[Dict]:
        """Get current user information."""
        if self._user_info is None:
            self.get_auth_status()
        return self._user_info

    def get_agent_config(self) -> Optional[Dict]:
        """Get current agent configuration."""
        if self._agent_config is None:
            self.get_auth_status()
        return self._agent_config

    def is_agent_authorized(self, agent_id: str) -> bool:
        """Check if the agent is authorized for the current user."""
        user_info = self.get_user_info()
        if not user_info:
            return False

        return user_info.get('agent_id') == agent_id

    def get_spending_limits(self) -> Dict:
        """Get spending limits from agent configuration."""
        config = self.get_agent_config()
        if not config:
            return {'max_budget': 0, 'remaining_budget': 0}

        max_budget = config.get('max_budget', 0)
        # In a real implementation, you'd track actual spending
        remaining_budget = max_budget  # Simplified for demo

        return {
            'max_budget': max_budget,
            'remaining_budget': remaining_budget,
            'currency': 'USD'
        }

    def is_agent_expired(self) -> bool:
        """Check if the agent authorization has expired."""
        config = self.get_agent_config()
        if not config:
            return True

        expiration_time_str = config.get('expiration_time')
        if not expiration_time_str:
            return True

        try:
            expiration_time = datetime.fromisoformat(expiration_time_str)
            return datetime.now() > expiration_time
        except Exception:
            return True

    def logout(self) -> bool:
        """Logout the current user."""
        try:
            response = self.session.post(f"{self.auth_server_url}/auth/logout")
            if response.status_code == 200:
                self._user_info = None
                self._agent_config = None
                return True
            return False
        except Exception as e:
            logging.error(f"Logout failed: {e}")
            return False

# Global auth client instance
auth_client = KiteAuthClient()


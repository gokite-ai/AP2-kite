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

"""Authentication middleware for the shopping agent."""

import json
import logging
from typing import Dict, Optional, Any
from flask import request, jsonify, redirect
from .auth_client import auth_client

class AuthMiddleware:
    """Middleware to handle authentication for the shopping agent."""

    def __init__(self):
        self.auth_client = auth_client

    def check_auth_required(self, endpoint: str) -> bool:
        """Check if authentication is required for the given endpoint."""
        # Define which endpoints require authentication
        protected_endpoints = [
            '/api/shop',
            '/api/payment',
            '/api/checkout',
            '/api/agent'
        ]

        return any(endpoint.startswith(protected) for protected in protected_endpoints)

    def get_auth_widget_html(self, username: Optional[str] = None) -> str:
        """Generate the authentication widget HTML for the top-right corner."""
        if username:
            # User is authenticated - show [logo] {username} with logout button
            return f"""
            <div id="auth-widget" style="position: fixed; top: 20px; right: 20px; z-index: 1000;">
                <div style="display: flex; align-items: center; gap: 8px; background: white; padding: 8px 16px; border-radius: 20px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); border: 1px solid #dee8c2;">
                    <img src="http://localhost:8004/auth/logo/kite" alt="Kite Logo" style="width: 20px; height: 20px;">
                    <span style="font-weight: 500; color: #485b10;">{username}</span>
                    <button id="logoutBtn" onclick="logout()" style="background: #485b10; color: white; border: none; padding: 6px 12px; border-radius: 12px; cursor: pointer; font-size: 12px; font-weight: 500; transition: background-color 0.2s;" onmouseover="this.style.background='#3a4a0d'" onmouseout="this.style.background='#485b10'">Logout</button>
                </div>
            </div>
            <script>
                function logout() {{
                    const logoutBtn = document.getElementById('logoutBtn');
                    logoutBtn.textContent = 'Logging out...';
                    logoutBtn.disabled = true;
                    logoutBtn.style.background = '#9ca3af';

                    // Redirect to auth server logout to properly clear session cookies
                    window.location.href = 'http://localhost:8004/auth/logout';
                }}
            </script>
            """
        else:
            # User is not authenticated - show [logo] Login
            return """
            <div id="auth-widget" style="position: fixed; top: 20px; right: 20px; z-index: 1000;">
                <a href="http://localhost:8004/auth/login" style="display: flex; align-items: center; gap: 8px; background: #485b10; color: white; padding: 8px 16px; border-radius: 20px; text-decoration: none; box-shadow: 0 2px 8px rgba(0,0,0,0.1); transition: background-color 0.2s;" onmouseover="this.style.background='#3a4a0d'" onmouseout="this.style.background='#485b10'">
                    <div style="width: 20px; height: 20px; background: white; border-radius: 4px; display: flex; align-items: center; justify-content: center;">
                        <img src="http://localhost:8004/auth/logo/kite" alt="Kite Logo" style="width: 16px; height: 16px;">
                    </div>
                    <span style="font-weight: 500;">Login</span>
                </a>
            </div>
            """

    def inject_auth_widget(self, html_content: str, request_cookies=None) -> str:
        """Inject the authentication widget into HTML content."""
        # Check authentication status with cookies
        if request_cookies:
            is_authenticated, user_info = self.auth_client.get_auth_status_with_cookies(request_cookies)
        else:
            is_authenticated, user_info = self.auth_client.get_auth_status()

        username = user_info.get('username') if is_authenticated else None

        # Generate auth widget
        auth_widget = self.get_auth_widget_html(username)

        # Inject into HTML
        if '<body>' in html_content:
            html_content = html_content.replace('<body>', f'<body>{auth_widget}')
        else:
            html_content = f'{auth_widget}{html_content}'

        return html_content

    def validate_agent_authorization(self, agent_id: str) -> Dict[str, Any]:
        """Validate agent authorization and return status."""
        is_authenticated, user_info = self.auth_client.get_auth_status()

        if not is_authenticated:
            return {
                'authorized': False,
                'reason': 'not_authenticated',
                'message': 'User not authenticated'
            }

        if not self.auth_client.is_agent_authorized(agent_id):
            return {
                'authorized': False,
                'reason': 'agent_not_authorized',
                'message': f'Agent {agent_id} not authorized for user {user_info.get("username")}'
            }

        if self.auth_client.is_agent_expired():
            return {
                'authorized': False,
                'reason': 'agent_expired',
                'message': 'Agent authorization has expired'
            }

        return {
            'authorized': True,
            'user_info': user_info,
            'agent_config': self.auth_client.get_agent_config()
        }

    def check_spending_limits(self, amount: float) -> Dict[str, Any]:
        """Check if the requested amount is within spending limits."""
        limits = self.auth_client.get_spending_limits()
        max_budget = limits.get('max_budget', 0)
        remaining_budget = limits.get('remaining_budget', 0)

        if amount > remaining_budget:
            return {
                'allowed': False,
                'reason': 'exceeds_budget',
                'message': f'Amount ${amount:.2f} exceeds remaining budget ${remaining_budget:.2f}',
                'limits': limits
            }

        return {
            'allowed': True,
            'limits': limits
        }

    def get_agent_context(self) -> Dict[str, Any]:
        """Get agent context including user info and configuration."""
        is_authenticated, user_info = self.auth_client.get_auth_status()

        if not is_authenticated:
            return {
                'authenticated': False,
                'agent_id': 'BuyWhenReady-gemini-anonymous',
                'username': 'anonymous',
                'spending_limits': {'max_budget': 0, 'remaining_budget': 0}
            }

        agent_config = self.auth_client.get_agent_config()
        spending_limits = self.auth_client.get_spending_limits()

        return {
            'authenticated': True,
            'agent_id': user_info.get('agent_id'),
            'username': user_info.get('username'),
            'agent_config': agent_config,
            'spending_limits': spending_limits
        }

# Global middleware instance
auth_middleware = AuthMiddleware()


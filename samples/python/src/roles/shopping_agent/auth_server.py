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

"""Authentication server for Kite integration with Privy login."""

import json
import logging
from datetime import datetime, timedelta
from typing import Dict, Optional
from flask import Flask, request, jsonify, redirect, session, render_template_string, send_file
from flask_cors import CORS
import uuid
import os
from .enhanced_config_template import ENHANCED_AGENT_CONFIG_TEMPLATE

app = Flask(__name__)
app.secret_key = 'kite-auth-secret-key-2025'
CORS(app)

# In-memory storage for demo purposes
# In production, this would be a proper database
users_db = {}
agent_configs = {}

# Logo paths
KITE_LOGO_PATH = "/Users/yusukemuraoka/workspace/codes/AP2-kite/samples/python/scenarios/a2a/human-present/kite/KiteLogo.png"
PRIVY_LOGO_PATH = "/Users/yusukemuraoka/workspace/codes/AP2-kite/samples/python/scenarios/a2a/human-present/kite/Privy_Brandmark_Black.svg"

# HTML templates
EMAIL_LOGIN_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Kite Login</title>
    <style>
        :root {
            --font-dm-sans: 'DM Sans', -apple-system, BlinkMacSystemFont, 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', 'Helvetica Neue', Helvetica, Arial, sans-serif;
        }
        body {
            font-family: var(--font-dm-sans);
            background: #fef8f1;
            margin: 0;
            padding: 0;
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .login-container {
            background: white;
            border-radius: 16px;
            padding: 40px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            max-width: 400px;
            width: 100%;
            margin: 20px;
            border: 1px solid #dee8c2;
        }
        .logo {
            text-align: center;
            margin-bottom: 30px;
        }
        .logo img {
            width: 48px;
            height: 48px;
        }
        .logo h1 {
            margin: 10px 0 0 0;
            color: #485b10;
            font-size: 24px;
            font-weight: 600;
        }
        .form-group {
            margin-bottom: 20px;
        }
        .form-group label {
            display: block;
            margin-bottom: 8px;
            color: #485b10;
            font-weight: 500;
        }
        .form-group input {
            width: 100%;
            padding: 12px 16px;
            border: 2px solid #efede5;
            border-radius: 8px;
            font-size: 16px;
            transition: border-color 0.2s;
            box-sizing: border-box;
            background: #fef8f1;
        }
        .form-group input:focus {
            outline: none;
            border-color: #485b10;
            background: white;
        }
        .login-btn {
            width: 100%;
            background: #485b10;
            color: white;
            border: none;
            padding: 14px;
            border-radius: 8px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: background-color 0.2s;
        }
        .login-btn:hover {
            background: #3a4a0d;
        }
        .login-btn:disabled {
            background: #9ca3af;
            cursor: not-allowed;
        }
        .error {
            color: #ef4444;
            font-size: 14px;
            margin-top: 8px;
        }
        .success {
            color: #10b981;
            font-size: 14px;
            margin-top: 8px;
        }
    </style>
</head>
<body>
    <div class="login-container">
        <div class="logo">
            <img src="/auth/logo/kite" alt="Kite Logo">
            <h1>Kite</h1>
        </div>

        <form id="emailForm">
            <div class="form-group">
                <label for="email">Email Address</label>
                <input type="email" id="email" name="email" placeholder="Enter your email address" required>
            </div>

            <button type="submit" class="login-btn" id="emailBtn">Continue</button>

            <div id="message"></div>
        </form>
    </div>

    <script>
        document.getElementById('emailForm').addEventListener('submit', function(e) {
            e.preventDefault();

            const email = document.getElementById('email').value;
            const messageDiv = document.getElementById('message');
            const emailBtn = document.getElementById('emailBtn');

            if (!email) {
                messageDiv.innerHTML = '<div class="error">Please enter your email address</div>';
                return;
            }

            emailBtn.disabled = true;
            emailBtn.textContent = 'Sending...';

            fetch('/auth/email', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ email })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    messageDiv.innerHTML = '<div class="success">Email sent! Redirecting to verification...</div>';
                    setTimeout(() => {
                        window.location.href = data.redirect_url;
                    }, 1000);
                } else {
                    messageDiv.innerHTML = '<div class="error">' + data.message + '</div>';
                    emailBtn.disabled = false;
                    emailBtn.textContent = 'Continue';
                }
            })
            .catch(error => {
                messageDiv.innerHTML = '<div class="error">Failed to send email. Please try again.</div>';
                emailBtn.disabled = false;
                emailBtn.textContent = 'Continue';
            });
        });
    </script>
</body>
</html>
"""

OTP_VERIFICATION_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Kite Verification</title>
    <style>
        :root {
            --font-dm-sans: 'DM Sans', -apple-system, BlinkMacSystemFont, 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', 'Helvetica Neue', Helvetica, Arial, sans-serif;
        }
        body {
            font-family: var(--font-dm-sans);
            background: #fef8f1;
            margin: 0;
            padding: 0;
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .verification-container {
            background: white;
            border-radius: 16px;
            padding: 40px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            max-width: 400px;
            width: 100%;
            margin: 20px;
            border: 1px solid #dee8c2;
        }
        .logo {
            text-align: center;
            margin-bottom: 30px;
        }
        .logo img {
            width: 48px;
            height: 48px;
        }
        .logo h1 {
            margin: 10px 0 0 0;
            color: #485b10;
            font-size: 24px;
            font-weight: 600;
        }
        .form-group {
            margin-bottom: 20px;
        }
        .form-group label {
            display: block;
            margin-bottom: 8px;
            color: #485b10;
            font-weight: 500;
        }
        .form-group input {
            width: 100%;
            padding: 12px 16px;
            border: 2px solid #efede5;
            border-radius: 8px;
            font-size: 16px;
            transition: border-color 0.2s;
            box-sizing: border-box;
            background: #fef8f1;
        }
        .form-group input:focus {
            outline: none;
            border-color: #485b10;
            background: white;
        }
        .otp-input {
            text-align: center;
            font-size: 18px;
            letter-spacing: 4px;
        }
        .verify-btn {
            width: 100%;
            background: #485b10;
            color: white;
            border: none;
            padding: 14px;
            border-radius: 8px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: background-color 0.2s;
        }
        .verify-btn:hover {
            background: #3a4a0d;
        }
        .verify-btn:disabled {
            background: #9ca3af;
            cursor: not-allowed;
        }
        .error {
            color: #ef4444;
            font-size: 14px;
            margin-top: 8px;
        }
        .success {
            color: #10b981;
            font-size: 14px;
            margin-top: 8px;
        }
        .privy-branding {
            text-align: center;
            margin-top: 20px;
            color: #485b10;
            font-size: 14px;
            background: #dee8c2;
            padding: 12px;
            border-radius: 8px;
        }
        .privy-branding img {
            width: 20px;
            height: 20px;
            vertical-align: middle;
            margin-right: 8px;
        }
    </style>
</head>
<body>
    <div class="verification-container">
        <div class="logo">
            <img src="/auth/logo/kite" alt="Kite Logo">
            <h1>Kite</h1>
        </div>

        <form id="otpForm">
            <div class="form-group">
                <label for="otp">Enter 6-digit verification code</label>
                <input type="text" id="otp" name="otp" class="otp-input" placeholder="000000" maxlength="6" pattern="[0-9]{6}">
            </div>

            <button type="submit" class="verify-btn" id="verifyBtn">Verify</button>

            <div id="message"></div>

            <div class="privy-branding">
                <img src="/auth/logo/privy" alt="Privy Logo">
                Powered by Privy
            </div>
        </form>
    </div>

    <script>
        document.getElementById('otp').addEventListener('input', function(e) {
            this.value = this.value.replace(/[^0-9]/g, '');
        });

        document.getElementById('otpForm').addEventListener('submit', function(e) {
            e.preventDefault();

            const otp = document.getElementById('otp').value;
            const messageDiv = document.getElementById('message');
            const verifyBtn = document.getElementById('verifyBtn');

            if (otp.length !== 6) {
                messageDiv.innerHTML = '<div class="error">Please enter a 6-digit code</div>';
                return;
            }

            verifyBtn.disabled = true;
            verifyBtn.textContent = 'Verifying...';

            fetch('/auth/verify', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ otp })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    messageDiv.innerHTML = '<div class="success">Verification successful! Redirecting...</div>';
                    setTimeout(() => {
                        window.location.href = data.redirect_url;
                    }, 1000);
                } else {
                    messageDiv.innerHTML = '<div class="error">' + data.message + '</div>';
                    verifyBtn.disabled = false;
                    verifyBtn.textContent = 'Verify';
                }
            })
            .catch(error => {
                messageDiv.innerHTML = '<div class="error">Verification failed. Please try again.</div>';
                verifyBtn.disabled = false;
                verifyBtn.textContent = 'Verify';
            });
        });
    </script>
</body>
</html>
"""

AGENT_CONFIG_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Agent Configuration</title>
    <style>
        body {
            font-family: 'Google Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            margin: 0;
            padding: 0;
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .config-container {
            background: white;
            border-radius: 16px;
            padding: 40px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            max-width: 500px;
            width: 100%;
            margin: 20px;
        }
        .logo {
            text-align: center;
            margin-bottom: 30px;
        }
        .logo svg {
            width: 48px;
            height: 48px;
        }
        .logo h1 {
            margin: 10px 0 0 0;
            color: #1a1a1a;
            font-size: 24px;
            font-weight: 600;
        }
        .form-group {
            margin-bottom: 20px;
        }
        .form-group label {
            display: block;
            margin-bottom: 8px;
            color: #374151;
            font-weight: 500;
        }
        .form-group input, .form-group select {
            width: 100%;
            padding: 12px 16px;
            border: 2px solid #e5e7eb;
            border-radius: 8px;
            font-size: 16px;
            transition: border-color 0.2s;
            box-sizing: border-box;
        }
        .form-group input:focus, .form-group select:focus {
            outline: none;
            border-color: #6366f1;
        }
        .form-row {
            display: flex;
            gap: 15px;
        }
        .form-row .form-group {
            flex: 1;
        }
        .config-btn {
            width: 100%;
            background: #6366f1;
            color: white;
            border: none;
            padding: 14px;
            border-radius: 8px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: background-color 0.2s;
        }
        .config-btn:hover {
            background: #5b5bd6;
        }
        .config-btn:disabled {
            background: #9ca3af;
            cursor: not-allowed;
        }
        .error {
            color: #ef4444;
            font-size: 14px;
            margin-top: 8px;
        }
        .success {
            color: #10b981;
            font-size: 14px;
            margin-top: 8px;
        }
        .agent-id {
            background: #f3f4f6;
            padding: 12px;
            border-radius: 8px;
            font-family: monospace;
            font-size: 14px;
            color: #374151;
        }
    </style>
</head>
<body>
    <div class="config-container">
        <div class="logo">
            <img src="/auth/logo/kite" alt="Kite Logo">
            <h1>Agent Configuration</h1>
        </div>

        <form id="configForm">
            <div class="form-group">
                <label>Agent Identifier</label>
                <div class="agent-id" id="agentId">BuyWhenReady-gemini-{{ username }}</div>
            </div>

            <div class="form-group">
                <label for="maxBudget">Maximum Budget ($)</label>
                <input type="number" id="maxBudget" name="maxBudget" min="1" max="10000" value="1000" required>
            </div>

            <div class="form-row">
                <div class="form-group">
                    <label for="expirationType">Expiration Type</label>
                    <select id="expirationType" name="expirationType" required>
                        <option value="duration">Duration</option>
                        <option value="datetime">Specific Date & Time</option>
                    </select>
                </div>
                <div class="form-group" id="durationGroup">
                    <label for="duration">Duration (hours)</label>
                    <input type="number" id="duration" name="duration" min="1" max="168" value="24">
                </div>
                <div class="form-group" id="datetimeGroup" style="display: none;">
                    <label for="expirationDate">Expiration Date</label>
                    <input type="datetime-local" id="expirationDate" name="expirationDate">
                </div>
            </div>

            <button type="submit" class="config-btn" id="configBtn">Configure Agent</button>

            <div id="message"></div>
        </form>
    </div>

    <script>
        const username = '{{ username }}';
        document.getElementById('agentId').textContent = `BuyWhenReady-gemini-${username}`;

        // Set default expiration date to 24 hours from now
        const now = new Date();
        now.setHours(now.getHours() + 24);
        document.getElementById('expirationDate').value = now.toISOString().slice(0, 16);

        document.getElementById('expirationType').addEventListener('change', function() {
            const durationGroup = document.getElementById('durationGroup');
            const datetimeGroup = document.getElementById('datetimeGroup');

            if (this.value === 'duration') {
                durationGroup.style.display = 'block';
                datetimeGroup.style.display = 'none';
            } else {
                durationGroup.style.display = 'none';
                datetimeGroup.style.display = 'block';
            }
        });

        document.getElementById('configForm').addEventListener('submit', function(e) {
            e.preventDefault();

            const maxBudget = document.getElementById('maxBudget').value;
            const expirationType = document.getElementById('expirationType').value;
            const duration = document.getElementById('duration').value;
            const expirationDate = document.getElementById('expirationDate').value;

            const messageDiv = document.getElementById('message');
            const configBtn = document.getElementById('configBtn');

            configBtn.disabled = true;
            configBtn.textContent = 'Configuring...';

            const configData = {
                username,
                maxBudget: parseFloat(maxBudget),
                expirationType,
                duration: parseInt(duration),
                expirationDate
            };

            fetch('/auth/configure', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(configData)
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    messageDiv.innerHTML = '<div class="success">Agent configured successfully! Redirecting...</div>';
                    setTimeout(() => {
                        window.location.href = data.redirect_url;
                    }, 1000);
                } else {
                    messageDiv.innerHTML = '<div class="error">' + data.message + '</div>';
                    configBtn.disabled = false;
                    configBtn.textContent = 'Configure Agent';
                }
            })
            .catch(error => {
                messageDiv.innerHTML = '<div class="error">Configuration failed. Please try again.</div>';
                configBtn.disabled = false;
                configBtn.textContent = 'Configure Agent';
            });
        });
    </script>
</body>
</html>
"""

@app.route('/auth/login', methods=['GET'])
def login_page():
    """Display the email login page."""
    return render_template_string(EMAIL_LOGIN_TEMPLATE)

@app.route('/auth/email', methods=['POST'])
def handle_email():
    """Handle email submission."""
    try:
        data = request.get_json()
        email = data.get('email')

        if not email:
            return jsonify({'success': False, 'message': 'Email is required'})

        # Store email in session for verification
        session['email'] = email
        session['username'] = 'ymuraoka'  # Fixed username as requested

        return jsonify({
            'success': True,
            'message': 'Email received',
            'redirect_url': '/auth/verify'
        })

    except Exception as e:
        logging.error(f"Email error: {e}")
        return jsonify({'success': False, 'message': 'Email processing failed. Please try again.'})

@app.route('/auth/verify', methods=['GET'])
def verify_page():
    """Display the OTP verification page."""
    return render_template_string(OTP_VERIFICATION_TEMPLATE)

@app.route('/auth/verify', methods=['POST'])
def verify_otp():
    """Handle OTP verification."""
    try:
        data = request.get_json()
        otp = data.get('otp')

        if not otp:
            return jsonify({'success': False, 'message': 'OTP is required'})

        # For demo purposes, accept any 6-digit OTP
        if len(otp) == 6 and otp.isdigit():
            # Create user session
            user_id = str(uuid.uuid4())
            email = session.get('email', 'user@example.com')
            username = session.get('username', 'ymuraoka')

            users_db[user_id] = {
                'username': username,
                'email': email,
                'login_time': datetime.now().isoformat(),
                'user_id': user_id
            }

            session['user_id'] = user_id

            return jsonify({
                'success': True,
                'message': 'Verification successful',
                'redirect_url': f'/auth/configure?username={username}'
            })
        else:
            return jsonify({'success': False, 'message': 'Invalid OTP. Please enter a 6-digit number.'})

    except Exception as e:
        logging.error(f"Verification error: {e}")
        return jsonify({'success': False, 'message': 'Verification failed. Please try again.'})

@app.route('/auth/configure', methods=['GET'])
def configure_page():
    """Display the agent configuration page."""
    username = request.args.get('username', 'ymuraoka')
    return render_template_string(ENHANCED_AGENT_CONFIG_TEMPLATE, username=username)

@app.route('/auth/configure', methods=['POST'])
def configure_agent():
    """Handle agent configuration."""
    try:
        data = request.get_json()
        username = data.get('username')
        session_name = data.get('sessionName')
        max_budget = data.get('maxBudget')
        expiration_type = data.get('expirationType')
        duration = data.get('duration')
        expiration_date = data.get('expirationDate')

        if not username:
            return jsonify({'success': False, 'message': 'Username is required'})

        # Calculate expiration time
        if expiration_type == 'duration':
            expiration_time = datetime.now() + timedelta(hours=duration)
        else:
            expiration_time = datetime.fromisoformat(expiration_date)

        # Create agent configuration
        agent_id = f"BuyWhenReady-gemini-{username}"
        agent_config = {
            'agent_id': agent_id,
            'username': username,
            'session_name': session_name or f"{agent_id}-{uuid.uuid4().hex[:8]}",
            'max_budget': max_budget,
            'expiration_time': expiration_time.isoformat(),
            'created_at': datetime.now().isoformat(),
            'status': 'active'
        }

        agent_configs[agent_id] = agent_config

        # Store in session
        session['agent_id'] = agent_id
        session['agent_config'] = agent_config

        return jsonify({
            'success': True,
            'message': 'Agent configured successfully',
            'redirect_url': '/auth/complete'
        })

    except Exception as e:
        logging.error(f"Configuration error: {e}")
        return jsonify({'success': False, 'message': 'Configuration failed. Please try again.'})

@app.route('/auth/complete', methods=['GET'])
def auth_complete():
    """Display completion page and redirect to shopping agent."""
    agent_id = session.get('agent_id')
    username = session.get('username')

    if not agent_id or not username:
        return redirect('/auth/login')

    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Authentication Complete</title>
        <style>
            :root {{
                --font-dm-sans: 'DM Sans', -apple-system, BlinkMacSystemFont, 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', 'Helvetica Neue', Helvetica, Arial, sans-serif;
            }}
            body {{
                font-family: var(--font-dm-sans);
                background: #fef8f1;
                margin: 0;
                padding: 0;
                min-height: 100vh;
                display: flex;
                align-items: center;
                justify-content: center;
            }}
            .complete-container {{
                background: white;
                border-radius: 16px;
                padding: 40px;
                box-shadow: 0 20px 40px rgba(0,0,0,0.1);
                text-align: center;
                max-width: 400px;
                border: 1px solid #dee8c2;
            }}
            .logo img {{
                width: 48px;
                height: 48px;
                margin-bottom: 20px;
            }}
            h1 {{
                color: #485b10;
                margin-bottom: 20px;
                font-size: 24px;
                font-weight: 600;
            }}
            p {{
                color: #485b10;
                font-size: 16px;
                margin-bottom: 15px;
            }}
            .redirect-info {{
                color: #485b10;
                font-size: 14px;
                background: #dee8c2;
                padding: 12px;
                border-radius: 8px;
                margin-top: 20px;
            }}
        </style>
    </head>
    <body>
        <div class="complete-container">
            <div class="logo">
                <img src="/auth/logo/kite" alt="Kite Logo">
            </div>
            <h1>✅ Authentication Complete</h1>
            <p>Welcome back, <strong>{username}</strong>!</p>
            <p class="redirect-info">Redirecting you back to the shopping agent...</p>
            <script>
                setTimeout(() => {{
                    window.location.href = 'http://localhost:8000';
                }}, 2000);
            </script>
        </div>
    </body>
    </html>
    """

@app.route('/auth/status', methods=['GET'])
def auth_status():
    """Check authentication status."""
    user_id = session.get('user_id')
    agent_id = session.get('agent_id')
    username = session.get('username')

    if user_id and agent_id and username:
        agent_config = agent_configs.get(agent_id, {})
        return jsonify({
            'authenticated': True,
            'username': username,
            'agent_id': agent_id,
            'agent_config': agent_config
        })
    else:
        return jsonify({'authenticated': False})

@app.route('/auth/logo/kite')
def serve_kite_logo():
    """Serve the Kite logo."""
    if os.path.exists(KITE_LOGO_PATH):
        return send_file(KITE_LOGO_PATH, mimetype='image/png')
    else:
        return "Logo not found", 404

@app.route('/auth/logo/privy')
def serve_privy_logo():
    """Serve the Privy logo."""
    if os.path.exists(PRIVY_LOGO_PATH):
        return send_file(PRIVY_LOGO_PATH, mimetype='image/svg+xml')
    else:
        return "Logo not found", 404

@app.route('/auth/logout', methods=['POST', 'GET'])
def logout():
    """Handle logout."""
    session.clear()

    # If it's a GET request (redirect from shopping agent), redirect back
    if request.method == 'GET':
        return redirect('http://localhost:8000')

    return jsonify({'success': True, 'message': 'Logged out successfully'})

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    app.run(host='0.0.0.0', port=8004, debug=True)


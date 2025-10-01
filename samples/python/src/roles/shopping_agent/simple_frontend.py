#!/usr/bin/env python3
"""
Simple Frontend for ADK with Kite Authentication
This module provides a simple HTML frontend that calls the ADK APIs directly.
"""

import logging
from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
import requests

from .auth_client import auth_client
from .auth_middleware import auth_middleware

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# ADK web interface URL
ADK_URL = "http://localhost:8001"

# Store active sessions
active_sessions = {}

# Simple HTML template
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Shopping Agent: BuyWhenReady</title>
    <style>
        :root {
            --font-sans: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
        }
        body {
            font-family: var(--font-sans);
            margin: 0;
            padding: 0;
            background: #0A0A07;
            min-height: 100vh;
            color: #92E4DD;
        }
        .container {
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
        }
        .header {
            text-align: center;
            margin-bottom: 30px;
            border-bottom: 2px solid #C4B643;
            padding-bottom: 20px;
        }
        .header h1 {
            color: #C4B643;
            margin-bottom: 10px;
            font-size: 28px;
            font-weight: bold;
        }
        .header p {
            color: #92E4DD;
            margin: 0;
            font-size: 14px;
        }
        .chat-container {
            background: rgba(18, 18, 15, 0.8);
            border: 1px solid #C4B643;
            border-radius: 12px;
            overflow: hidden;
            box-shadow: 0 0 20px rgba(196, 182, 67, 0.1);
        }
        .chat-messages {
            height: 400px;
            overflow-y: auto;
            padding: 20px;
            border-bottom: 1px solid #C4B643;
            background: rgba(10, 10, 7, 0.5);
        }
        .message {
            margin-bottom: 15px;
            padding: 12px 16px;
            border-radius: 8px;
            max-width: 80%;
            font-size: 14px;
            line-height: 1.4;
        }
        .user-message {
            background: rgba(146, 228, 221, 0.1);
            color: #92E4DD;
            margin-left: auto;
            border: 1px solid rgba(146, 228, 221, 0.3);
        }
        .agent-message {
            background: rgba(196, 182, 67, 0.1);
            color: #C4B643;
            border: 1px solid rgba(196, 182, 67, 0.3);
        }
        .agent-message strong {
            color: #C4B643;
        }
        .user-message strong {
            color: #92E4DD;
        }
        .chat-input {
            display: flex;
            padding: 20px;
            gap: 10px;
            background: rgba(10, 10, 7, 0.8);
        }
        .chat-input input {
            flex: 1;
            padding: 12px 16px;
            border: 1px solid #C4B643;
            border-radius: 6px;
            font-size: 14px;
            background: rgba(10, 10, 7, 0.8);
            color: #92E4DD;
            font-family: var(--font-sans);
        }
        .chat-input input:focus {
            outline: none;
            border-color: #C4B643;
            box-shadow: 0 0 5px rgba(196, 182, 67, 0.3);
        }
        .chat-input input::placeholder {
            color: rgba(146, 228, 221, 0.6);
        }
        .chat-input button {
            background: #C4B643;
            color: #0A0A07;
            border: none;
            padding: 12px 24px;
            border-radius: 6px;
            cursor: pointer;
            font-size: 14px;
            font-family: var(--font-sans);
            font-weight: bold;
            transition: background-color 0.2s;
        }
        .chat-input button:hover {
            background: #B8A83A;
        }
        .chat-input button:disabled {
            background: rgba(196, 182, 67, 0.3);
            cursor: not-allowed;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Shopping Agent: "BuyWhenReady"</h1>
            <p>Powered by Kite</p>
        </div>

        <div class="chat-container">
            <div class="chat-messages" id="chatMessages">
                <div class="message agent-message">
                    <strong>BuyWhenReady:</strong><br>
                    Hi! I'm BuyWhenReady, your shopping assistant.
                    How can I help you today? For example, you can say "I want to buy a pair of shoes"
                </div>
            </div>

            <div class="chat-input">
                <input type="text" id="messageInput" placeholder="Type your message..." onkeypress="handleKeyPress(event)">
                <button onclick="sendMessage()" id="sendButton">Send</button>
            </div>
        </div>

    </div>

    <script>
        function handleKeyPress(event) {
            if (event.key === 'Enter') {
                sendMessage();
            }
        }

        function sendMessage() {
            const input = document.getElementById('messageInput');
            const message = input.value.trim();

            if (!message) return;

            // Add user message to chat
            addMessage(message, 'user');

            // Clear input and disable button
            input.value = '';
            const sendButton = document.getElementById('sendButton');
            sendButton.disabled = true;
            sendButton.textContent = 'Sending...';

            // Send to agent
            fetch('/api/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ message })
            })
            .then(response => response.json())
            .then(data => {
                addMessage(data.response, 'agent');
            })
            .catch(error => {
                addMessage('Sorry, I encountered an error. Please try again.', 'agent');
            })
            .finally(() => {
                sendButton.disabled = false;
                sendButton.textContent = 'Send';
            });
        }

        function addMessage(text, type) {
            const messagesContainer = document.getElementById('chatMessages');
            const messageDiv = document.createElement('div');
            messageDiv.className = `message ${type}-message`;

            if (type === 'user') {
                messageDiv.innerHTML = `<strong>You:</strong><br>${text}`;
            } else {
                messageDiv.innerHTML = `<strong>BuyWhenReady:</strong><br>${text}`;
            }

            messagesContainer.appendChild(messageDiv);
            messagesContainer.scrollTop = messagesContainer.scrollHeight;
        }
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    """Main shopping agent interface."""
    # Get authentication status
    is_authenticated, user_info = auth_client.get_auth_status()
    username = user_info.get('username') if is_authenticated else None

    # Generate the main interface HTML
    html_content = HTML_TEMPLATE

    # Inject authentication widget
    html_content = auth_middleware.inject_auth_widget(html_content, request.cookies)

    return html_content

@app.route('/api/chat', methods=['POST'])
def chat_with_agent():
    """Handle chat messages by calling the ADK /run endpoint."""
    try:
        data = request.get_json()
        message = data.get('message', '')
        user_id = data.get('user_id', 'default_user')

        # Get authentication status
        is_authenticated, user_info = auth_client.get_auth_status_with_cookies(request.cookies)
        username = user_info.get('username') if is_authenticated else 'anonymous'

        # Create a unique session key for this user
        session_key = f"{username}_{user_id}"

        # Check if we already have a session for this user
        if session_key in active_sessions:
            session_id = active_sessions[session_key]
            logger.info(f"Using existing session: {session_id}")
        else:
            # Create a new session
            try:
                session_response = requests.post(
                    f"{ADK_URL}/apps/shopping_agent/users/{user_id}/sessions",
                    json={},
                    timeout=10
                )
                if session_response.status_code == 200:
                    session_data = session_response.json()
                    session_id = session_data['id']
                    active_sessions[session_key] = session_id
                    logger.info(f"Created new session: {session_id}")
                else:
                    logger.warning(f"Failed to create session: {session_response.status_code}")
                    session_id = f"session_{username}_{user_id}"
            except Exception as e:
                logger.warning(f"Could not create session, using default: {e}")
                session_id = f"session_{username}_{user_id}"

        # Prepare the message for ADK
        adk_message = {
            "appName": "shopping_agent",
            "userId": user_id,
            "sessionId": session_id,
            "newMessage": {
                "parts": [
                    {
                        "text": message
                    }
                ],
                "role": "user"
            },
            "streaming": False
        }

        logger.info(f"Calling ADK /run with session: {session_id}")

        # Call the ADK /run endpoint
        response = requests.post(
            f"{ADK_URL}/run",
            json=adk_message,
            timeout=30
        )

        if response.status_code == 200:
            events = response.json()
            logger.info(f"ADK returned {len(events)} events")

            # Extract the response from the events
            response_text = ""
            for event in events:
                if event.get('content') and isinstance(event['content'], dict):
                    content = event['content']
                    if 'parts' in content:
                        for part in content['parts']:
                            if 'text' in part and part['text']:
                                response_text += part['text']

            logger.info(f"Extracted response: {response_text[:100]}...")

            return jsonify({
                'response': response_text or "I received your message but couldn't generate a response.",
                'agent_id': user_info.get('agent_id', 'BuyWhenReady-gemini-anonymous') if is_authenticated else 'BuyWhenReady-gemini-anonymous',
                'authenticated': is_authenticated
            })
        else:
            logger.error(f"ADK /run endpoint error: {response.status_code} - {response.text}")
            return jsonify({
                'response': "Sorry, I encountered an error processing your request.",
                'agent_id': 'BuyWhenReady-gemini-anonymous',
                'authenticated': False
            }), 500

    except Exception as e:
        logger.error(f"Error in chat_with_agent: {e}")
        return jsonify({
            'response': f"Sorry, I encountered an error: {str(e)}",
            'agent_id': 'BuyWhenReady-gemini-anonymous',
            'authenticated': False
        }), 500

@app.route('/auth/status')
def auth_status():
    """Check authentication status."""
    try:
        is_authenticated, user_info = auth_client.get_auth_status_with_cookies(request.cookies)
        if is_authenticated:
            return jsonify({
                'authenticated': True,
                'username': user_info.get('username'),
                'agent_id': user_info.get('agent_id'),
                'agent_config': user_info.get('agent_config')
            })
        return jsonify({'authenticated': False})
    except Exception as e:
        logger.error(f"Error checking auth status: {e}")
        return jsonify({'authenticated': False, 'error': str(e)}), 500

@app.route('/auth/logout', methods=['POST', 'GET'])
def logout():
    """Handle logout."""
    try:
        # Clear session on auth server
        response = requests.post("http://localhost:8004/auth/logout")

        if request.method == 'GET':
            return redirect("http://localhost:8000")

        return jsonify({'success': True, 'message': 'Logged out successfully'})
    except Exception as e:
        logger.error(f"Error during logout: {e}")
        return jsonify({'error': 'Logout failed'}), 500

def main():
    """Main function to start the simple frontend server."""
    logger.info("Starting simple frontend server on port 8000...")
    app.run(host='0.0.0.0', port=8000, debug=False)

if __name__ == "__main__":
    main()

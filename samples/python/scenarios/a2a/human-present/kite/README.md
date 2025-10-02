# Enhanced AP2-Kite Demo with Authentication (Kite + ADK)

This demo showcases AP2-Kite integration where a custom frontend (port 8000) provides chat + Kite login, while the original ADK agent logic is used via ADK APIs (port 8001). The system includes a complete multi-agent architecture with proper port management and authentication integration.

## Features

### 🔐 Authentication
- **Kite Login**: Dedicated login page with Kite branding
- **OTP Authentication**: 6-digit code verification (demo accepts any code)
- **Session Management**: Secure Flask sessions

### 🤖 Agent Configuration
- **Agent ID**: `BuyWhenReady-gemini-{username}` format
- **Spending Limits**: Configurable maximum budget
- **Expiration**: Set by duration or specific date/time

### 🎨 Enhanced UI
- **Auth Widget**: Top-right corner with login status
- **Kite Logo**: Branded interface
- **Responsive**: Modern, mobile-friendly design

## Usage

Start with the one-shot launcher (recommended):

```bash
samples/python/scenarios/a2a/human-present/kite/run_all.sh
```

Or start the three services manually in separate terminals:

1) ADK Web (agent logic, port 8001)

```bash
uv run --package ap2-samples adk web --host 0.0.0.0 --port 8001 samples/python/src/roles
```

2) Kite Authentication Server (port 8004)

```bash
uv run --package ap2-samples python -m roles.shopping_agent.auth_server
```

3) Custom Frontend (port 8000)

```bash
uv run --package ap2-samples python -m roles.shopping_agent.simple_frontend
```

Then:
- Open `http://localhost:8000`
- Click Login (email → OTP 6 digits; any number passes for demo)
- Configure session (wallet info, session name, budget, expiration)
- Chat with the agent; conversation memory is preserved per user session

## Architecture

The system uses a multi-service architecture with proper port management:

- **Port 8000 - Custom Frontend (`simple_frontend.py`)**
  - Renders chat UI (BuyWhenReady) with dark theme and Monaco font
  - Injects Kite authentication widget in top-right corner
  - Calls ADK APIs via `/apps/.../sessions` and `/run` for agent interaction
  - Maintains conversation memory by reusing stable ADK `sessionId` per `{username}_{user_id}`
  - Renders agent responses with Markdown support for better readability

- **Port 8001 - ADK Web Interface**
  - Hosts the original agent applications and provides `/run` and session APIs
  - Manages the core shopping agent logic and conversation state
  - Provides endpoints for agent interaction and session management

- **Port 8004 - Kite Authentication Server (`auth_server.py`)**
  - Email → OTP (6 digits, demo) → Session Configuration flow
  - Stores `username`, `agent_id = BuyWhenReady-gemini-{username}`, and `agent_config` in session
  - Serves Kite and Privy logos for branding
  - Handles logout and session management

- **Port 8006 - Merchant Agent**
  - Provides product search functionality
  - Handles product catalog searches and cart mandate creation
  - Required for the shopping agent to find products (resolves "searching" state issues)

- **Port 8002 - Credentials Provider Agent**
  - Manages payment credentials and authentication

- **Port 8003 - Card Processor Agent**
  - Handles payment processing and transaction management

## Security

- Session-based authentication on the auth server
- Agent authorization validation (demo-level)
- Budget/expiration captured as session configuration (demo-level)

## Technical Approach

### Key Design Decisions

1. **Custom Frontend vs ADK Proxy**: We chose a custom Flask frontend that calls ADK APIs directly rather than proxying the ADK web interface. This provides better control over the UI and authentication integration.

2. **Port Management**: Resolved port conflicts by assigning specific ports to each service:
   - ADK Web: 8001 (core agent logic)
   - Merchant Agent: 8006 (product search)
   - Auth Server: 8004 (authentication)
   - Frontend: 8000 (user interface)

3. **Authentication Integration**: The authentication system is injected as a widget into the custom frontend, allowing seamless login/logout without disrupting the chat experience.

4. **Session Management**: The system maintains conversation memory by creating and reusing ADK sessions per user, ensuring the agent remembers previous conversation turns.

### Issues Resolved

1. **Google AI API Key Issue**: Fixed the `base_server_executor.py` to properly initialize the Google AI client with the API key from environment variables.

2. **Port Conflicts**: Resolved conflicts between ADK web interface and merchant agent by assigning them to different ports (8001 vs 8006).

3. **Agent "Searching" State**: The shopping agent was getting stuck in a "searching" state because it couldn't communicate with the merchant agent. This was resolved by ensuring all required agents are running on their correct ports.

4. **Environment Variable Loading**: Fixed issues with environment variables not being passed correctly to background processes in the startup script.

### File Structure

- `run_all.sh`: One-shot launcher for all services
- `simple_frontend.py`: Custom Flask frontend with authentication integration
- `auth_server.py`: Kite authentication server
- `auth_client.py`: Client for authentication communication
- `auth_middleware.py`: Middleware for authentication widget injection
- `enhanced_config_template.py`: Enhanced configuration page template

## Notes

- We do not proxy or render the ADK Dev UI; instead, the custom frontend calls ADK APIs directly.
- Removed legacy files: `adk_proxy.py`, `adk_integration.py`, `enhanced_agent.py`, `agent_service.py`, and their run scripts.
- The system requires all agents to be running for full functionality (merchant agent for product search, credentials provider for payment, etc.).

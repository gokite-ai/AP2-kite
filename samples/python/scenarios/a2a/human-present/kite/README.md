# Enhanced AP2-Kite Demo with Authentication (Kite + ADK)

This demo showcases AP2-Kite integration where a custom frontend (port 8000) provides chat + Kite login, while the original ADK agent logic is used via ADK APIs (port 8001).

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

- **Port 8000 - Custom Frontend (`simple_frontend.py`)**
  - Renders chat UI (BuyWhenReady) and injects Kite auth widget
  - Calls ADK via `/apps/.../sessions` and `/run`
  - Maintains conversation memory by reusing a stable ADK `sessionId` per `{username}_{user_id}`
- **Port 8001 - ADK Web**
  - Hosts the original agent apps; provides `/run` and session APIs
- **Port 8004 - Kite Auth Server**
  - Email → OTP (6 digits, demo) → Session Configuration (wallet, session name, budget, expiration)
  - Stores `username`, `agent_id = BuyWhenReady-gemini-{username}`, and `agent_config` in session

## Security

- Session-based authentication on the auth server
- Agent authorization validation (demo-level)
- Budget/expiration captured as session configuration (demo-level)

## Notes

- We do not proxy or render the ADK Dev UI; instead, the custom frontend calls ADK APIs directly.
- Removed legacy files: `adk_proxy.py`, `adk_integration.py`, `enhanced_agent.py`, `agent_service.py`, and their run scripts.

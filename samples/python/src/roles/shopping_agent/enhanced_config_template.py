# Enhanced Agent Configuration Template with Wallet and Session Management

ENHANCED_AGENT_CONFIG_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Agent Configuration</title>
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
        .config-container {
            background: white;
            border-radius: 16px;
            padding: 30px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            max-width: 600px;
            width: 100%;
            margin: 20px;
            border: 1px solid #dee8c2;
        }
        .logo {
            text-align: center;
            margin-bottom: 20px;
        }
        .logo img {
            width: 32px;
            height: 32px;
        }
        .logo h1 {
            margin: 8px 0 0 0;
            color: #1a1a1a;
            font-size: 20px;
            font-weight: 600;
        }
        .section {
            margin-bottom: 25px;
            padding: 20px;
            border: 1px solid #dee8c2;
            border-radius: 12px;
            background: #fef8f1;
        }
        .section-title {
            font-size: 16px;
            font-weight: 600;
            color: #485b10;
            margin-bottom: 15px;
            display: flex;
            align-items: center;
            gap: 8px;
        }
        .section-icon {
            width: 20px;
            height: 20px;
        }
        .form-group {
            margin-bottom: 15px;
        }
        .form-group label {
            display: block;
            margin-bottom: 6px;
            color: #485b10;
            font-weight: 500;
            font-size: 14px;
        }
        .form-group input, .form-group select {
            width: 100%;
            padding: 10px 12px;
            border: 1px solid #efede5;
            border-radius: 6px;
            font-size: 14px;
            transition: border-color 0.2s;
            box-sizing: border-box;
            background: #fef8f1;
        }
        .form-group input:focus, .form-group select:focus {
            outline: none;
            border-color: #485b10;
            background: white;
        }
        .form-row {
            display: flex;
            gap: 12px;
        }
        .form-row .form-group {
            flex: 1;
        }
        .user-info {
            display: flex;
            flex-direction: column;
            gap: 12px;
        }
        .user-name {
            font-size: 16px;
            color: #485b10;
        }
        .wallet-info {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 12px;
            background: white;
            border-radius: 8px;
            border: 1px solid #dee8c2;
        }
        .agent-id-display {
            padding: 12px;
            background: white;
            border-radius: 8px;
            border: 1px solid #dee8c2;
        }
        .wallet-address {
            font-family: monospace;
            font-size: 12px;
            color: #485b10;
        }
        .wallet-balance {
            font-weight: 600;
            color: #485b10;
        }
        .session-name {
            display: flex;
            align-items: center;
            gap: 8px;
        }
        .session-name input {
            flex: 1;
        }
        .edit-btn {
            background: #dee8c2;
            border: 1px solid #485b10;
            color: #485b10;
            padding: 6px 12px;
            border-radius: 4px;
            font-size: 12px;
            cursor: pointer;
            transition: background-color 0.2s;
        }
        .edit-btn:hover {
            background: #c5d4a8;
        }
        .config-btn {
            width: 100%;
            background: #485b10;
            color: white;
            border: none;
            padding: 12px;
            border-radius: 8px;
            font-size: 14px;
            font-weight: 600;
            cursor: pointer;
            transition: background-color 0.2s;
        }
        .config-btn:hover {
            background: #3a4a0d;
        }
        .config-btn:disabled {
            background: #9ca3af;
            cursor: not-allowed;
        }
        .error {
            color: #ef4444;
            font-size: 12px;
            margin-top: 6px;
        }
        .success {
            color: #10b981;
            font-size: 12px;
            margin-top: 6px;
        }
        .agent-id {
            background: #dee8c2;
            padding: 8px 12px;
            border-radius: 6px;
            font-family: monospace;
            font-size: 12px;
            color: #485b10;
        }
    </style>
</head>
<body>
    <div class="config-container">
        <div class="logo">
            <img src="/auth/logo/kite" alt="Kite Logo">
            <h1>Session Configuration</h1>
        </div>

        <form id="configForm">
            <!-- Login User Section -->
            <div class="section">
                <div class="section-title">
                    <svg class="section-icon" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path d="M20 21V19C20 17.9391 19.5786 16.9217 18.8284 16.1716C18.0783 15.4214 17.0609 15 16 15H8C6.93913 15 5.92172 15.4214 5.17157 16.1716C4.42143 16.9217 4 17.9391 4 19V21" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                        <path d="M12 11C14.2091 11 16 9.20914 16 7C16 4.79086 14.2091 3 12 3C9.79086 3 8 4.79086 8 7C8 9.20914 9.79086 11 12 11Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                    </svg>
                    Login User
                </div>
                <div class="user-info">
                    <div class="user-name">
                        <strong>{{ username }}</strong>
                    </div>
                    <div class="wallet-info">
                        <div class="wallet-address" id="walletAddress">0x742d35Cc6634C0532925a3b8D</div>
                        <div class="wallet-balance" id="walletBalance">$2,847.32</div>
                    </div>
                </div>
            </div>

            <!-- Agent ID Section -->
            <div class="section">
                <div class="section-title">
                    <svg class="section-icon" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path d="M12 2L2 7L12 12L22 7L12 2Z" stroke="currentColor" stroke-width="2" stroke-linejoin="round"/>
                        <path d="M2 17L12 22L22 17" stroke="currentColor" stroke-width="2" stroke-linejoin="round"/>
                        <path d="M2 12L12 17L22 12" stroke="currentColor" stroke-width="2" stroke-linejoin="round"/>
                    </svg>
                    Agent ID
                </div>
                <div class="agent-id-display">
                    <div class="agent-id" id="agentId">BuyWhenReady-gemini-{{ username }}</div>
                </div>
            </div>

            <!-- Session Section -->
            <div class="section">
                <div class="section-title">
                    <svg class="section-icon" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path d="M12 15C13.6569 15 15 13.6569 15 12C15 10.3431 13.6569 9 12 9C10.3431 9 9 10.3431 9 12C9 13.6569 10.3431 15 12 15Z" stroke="currentColor" stroke-width="2"/>
                        <path d="M19.4 15C19.2669 15.3016 19.2272 15.6362 19.286 15.9606C19.3448 16.285 19.4995 16.5843 19.73 16.82L19.79 16.88C19.976 17.0657 20.1235 17.2863 20.2241 17.5291C20.3248 17.7719 20.3766 18.0322 20.3766 18.295C20.3766 18.5578 20.3248 18.8181 20.2241 19.0609C20.1235 19.3037 19.976 19.5243 19.79 19.71C19.6043 19.896 19.3837 20.0435 19.1409 20.1441C18.8981 20.2448 18.6378 20.2966 18.375 20.2966C18.1122 20.2966 17.8519 20.2448 17.6091 20.1441C17.3663 20.0435 17.1457 19.896 16.96 19.71L16.9 19.65C16.6643 19.4195 16.365 19.2648 16.0406 19.206C15.7162 19.1472 15.3816 19.1869 15.08 19.32C14.7842 19.4468 14.532 19.6572 14.3543 19.9255C14.1766 20.1938 14.0813 20.5082 14.08 20.83V21C14.08 21.5304 13.8693 22.0391 13.4942 22.4142C13.1191 22.7893 12.6104 23 12.08 23C11.5496 23 11.0409 22.7893 10.6658 22.4142C10.2907 22.0391 10.08 21.5304 10.08 21V20.91C10.0723 20.579 9.96512 20.2573 9.77251 19.9887C9.5799 19.7201 9.31074 19.5166 9 19.41C8.68926 19.3034 8.4201 19.0999 8.22749 18.8313C8.03488 18.5627 7.92772 18.241 7.92 17.91V17C7.92 16.4696 7.70929 15.9609 7.33421 15.5858C6.95914 15.2107 6.45043 15 5.92 15C5.38957 15 4.88086 15.2107 4.50579 15.5858C4.13071 15.9609 3.92 16.4696 3.92 17V17.09C3.91827 17.4209 3.81112 17.7426 3.61851 18.0113C3.4259 18.2799 3.15674 18.4834 2.846 18.59C2.53526 18.6966 2.2661 18.9001 2.07349 19.1687C1.88088 19.4373 1.77372 19.759 1.766 20.09V21C1.766 21.5304 1.55529 22.0391 1.18021 22.4142C0.80514 22.7893 0.29643 23 -0.234 23C-0.76443 23 -1.27314 22.7893 -1.64821 22.4142C-2.02329 22.0391 -2.234 21.5304 -2.234 21V20.83C-2.23527 20.5082 -2.33059 20.1938 -2.50828 19.9255C-2.68597 19.6572 -2.93816 19.4468 -3.234 19.32C-3.53562 19.1869 -3.87018 19.1472 -4.19458 19.206C-4.51898 19.2648 -4.8183 19.4195 -5.054 19.65L-5.114 19.71C-5.29974 19.896 -5.52034 20.0435 -5.76314 20.1441C-6.00594 20.2448 -6.26624 20.2966 -6.529 20.2966C-6.79176 20.2966 -7.05206 20.2448 -7.29486 20.1441C-7.53766 20.0435 -7.75826 19.896 -7.944 19.71C-8.12974 19.5243 -8.27724 19.3037 -8.37786 19.0609C-8.47848 18.8181 -8.53024 18.5578 -8.53024 18.295C-8.53024 18.0322 -8.47848 17.7719 -8.37786 17.5291C-8.27724 17.2863 -8.12974 17.0657 -7.944 16.88L-7.884 16.82C-7.65354 16.5843 -7.49885 16.285 -7.44002 15.9606C-7.38119 15.6362 -7.42089 15.3016 -7.554 15H-7.554Z" stroke="currentColor" stroke-width="2"/>
                    </svg>
                    Session
                </div>

                <div class="form-group">
                    <label for="sessionName">Session Name</label>
                    <div class="session-name">
                        <input type="text" id="sessionName" name="sessionName" placeholder="Enter session name" readonly>
                        <button type="button" class="edit-btn" id="editSessionBtn" onclick="toggleSessionEdit()">Edit</button>
                    </div>
                </div>

                <div class="form-group">
                    <label for="maxBudget">Budget ($)</label>
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
            </div>

            <button type="submit" class="config-btn" id="configBtn">Configure Session</button>

            <div id="message"></div>
        </form>
    </div>

    <script>
        const username = '{{ username }}';
        const agentId = `BuyWhenReady-gemini-${username}`;
        const randomHash = Math.random().toString(36).substring(2, 8);
        const defaultSessionName = `${agentId}-${randomHash}`;

        // Set agent ID display
        document.getElementById('agentId').textContent = agentId;

        // Set session name
        document.getElementById('sessionName').value = defaultSessionName;

        // Set default expiration date to 24 hours from now
        const now = new Date();
        now.setHours(now.getHours() + 24);
        document.getElementById('expirationDate').value = now.toISOString().slice(0, 16);

        function toggleSessionEdit() {
            const sessionInput = document.getElementById('sessionName');
            const editBtn = document.getElementById('editSessionBtn');

            if (sessionInput.readOnly) {
                sessionInput.readOnly = false;
                sessionInput.focus();
                editBtn.textContent = 'Save';
            } else {
                sessionInput.readOnly = true;
                editBtn.textContent = 'Edit';
            }
        }

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
            const sessionName = document.getElementById('sessionName').value;

            const messageDiv = document.getElementById('message');
            const configBtn = document.getElementById('configBtn');

            configBtn.disabled = true;
            configBtn.textContent = 'Configuring Session...';

            const configData = {
                username,
                sessionName,
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
                    messageDiv.innerHTML = '<div class="success">Session configured successfully! Redirecting...</div>';
                    setTimeout(() => {
                        window.location.href = data.redirect_url;
                    }, 1000);
                } else {
                    messageDiv.innerHTML = '<div class="error">' + data.message + '</div>';
                    configBtn.disabled = false;
                    configBtn.textContent = 'Configure Session';
                }
            })
            .catch(error => {
                messageDiv.innerHTML = '<div class="error">Configuration failed. Please try again.</div>';
                configBtn.disabled = false;
                configBtn.textContent = 'Configure Session';
            });
        });
    </script>
</body>
</html>
"""

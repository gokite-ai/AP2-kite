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

"""Tools used by the payment method collector subagent.

Each agent uses individual tools to handle distinct tasks throughout the
shopping and purchasing process.
"""

from google.adk.tools.tool_context import ToolContext

from ap2.types.payment_request import PAYMENT_METHOD_DATA_DATA_KEY
from common.a2a_message_builder import A2aMessageBuilder
import os
from common import artifact_utils
from roles.shopping_agent.remote_agents import credentials_provider_client


async def get_payment_methods(
    user_email: str,
    tool_context: ToolContext,
) -> list[str]:
  """Gets the user's payment methods - returns Kite wallet for demo.

  Args:
    user_email: Identifies the user's account
    tool_context: The ADK supplied tool context.

  Returns:
    A list containing the Kite wallet payment method.
  """
  # For demo purposes, always return Kite User Wallet as the payment method
  return ["Kite User Wallet"]


async def get_payment_credential_token(
    user_email: str,
    payment_method_alias: str,
    tool_context: ToolContext,
) -> str:
  """Gets a payment credential token - returns demo token for Kite wallet.

  Args:
    user_email: The user's email address.
    payment_method_alias: The payment method alias.
    tool_context: The ADK supplied tool context.

  Returns:
    Status of the call and the payment credential token.
  """
  # Demo fallback: if user_email not provided, use DEMO_USER_EMAIL or a default
  user_email = user_email or os.getenv("DEMO_USER_EMAIL", "bugsbunny@gmail.com")

  # For Kite User Wallet, create a demo token
  if payment_method_alias == "Kite User Wallet":
    demo_token = {
        "type": "kite_wallet",
        "address": "0x742d35Cc6634C0532925a3b8D",
        "balance": 2847.32,
        "currency": "USD"
    }

    tool_context.state["payment_credential_token"] = {
        "value": demo_token,
        "url": "demo://kite-wallet",
    }
    return {"status": "success", "token": demo_token}

  # Fallback to credentials provider for other payment methods
  message = (
      A2aMessageBuilder()
      .set_context_id(tool_context.state["shopping_context_id"])
      .add_text("Get a payment credential token for the user's payment method.")
      .add_data("payment_method_alias", payment_method_alias)
      .add_data("user_email", user_email)
      .build()
  )
  task = await credentials_provider_client.send_a2a_message(message)
  data = artifact_utils.get_first_data_part(task.artifacts)
  token = data.get("token")
  credentials_provider_agent_card = (
      await credentials_provider_client.get_agent_card()
  )

  tool_context.state["payment_credential_token"] = {
      "value": token,
      "url": credentials_provider_agent_card.url,
  }
  return {"status": "success", "token": token}

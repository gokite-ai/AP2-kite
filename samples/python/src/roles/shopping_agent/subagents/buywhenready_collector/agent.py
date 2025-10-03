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

"""An agent responsible for collecting BuyWhenReady conditions from the user.

The shopping agent delegates responsibility for collecting the user's BuyWhenReady
conditions to this subagent when the user chooses to use BuyWhenReady instead of
immediate purchase.

This agent collects the specific conditions the user wants to wait for before
the purchase is automatically executed.
"""

from . import tools
from common.retrying_llm_agent import RetryingLlmAgent
from common.system_utils import DEBUG_MODE_INSTRUCTIONS


buywhenready_collector = RetryingLlmAgent(
    model="gemini-2.5-flash",
    name="buywhenready_collector",
    max_retries=1,
    delay_between_calls=2.0,
    instruction="""
    You are an agent responsible for collecting the user's BuyWhenReady conditions.

    %s

    When asked to collect BuyWhenReady conditions, follow these instructions:
    1. Explain: "BuyWhenReady allows you to set up automatic purchase conditions.
       When your specified conditions are met, the purchase will be executed automatically."

    2. Ask the user what conditions they want to set up. Offer these options:
       - Price drops below a specific amount
       - Price drops by a certain percentage
       - Purchase at a specific date/time
       - Item becomes available in stock

    3. Collect the specific details for their chosen condition.

    4. Present a summary of the conditions for confirmation.

    5. Store the confirmed conditions using the store_buywhenready_conditions tool.

    6. Return to the root agent with the confirmed conditions.
    """ % DEBUG_MODE_INSTRUCTIONS,
    tools=[
        tools.store_buywhenready_conditions,
    ],
)

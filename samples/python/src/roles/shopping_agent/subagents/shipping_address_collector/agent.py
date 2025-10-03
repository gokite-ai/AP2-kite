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

"""An agent responsible for collecting the user's shipping address.

The shopping agent delegates responsibility for collecting the user's shipping
address to this subagent, after the user has chosen a product.

In this sample, the shopping agent assumes it must collect the shipping address
before finalizing the cart, as it may impact costs such as shipping and tax.

Also in this sample, the shopping agent offers the user the option of using a
digital wallet to provide their shipping address.

This is just one of many possible approaches.
"""

from . import tools
from common.retrying_llm_agent import RetryingLlmAgent
from common.system_utils import DEBUG_MODE_INSTRUCTIONS

shipping_address_collector = RetryingLlmAgent(
    model="gemini-2.5-flash",
    name="shipping_address_collector",
    max_retries=2,
    delay_between_calls=1.5,
    instruction="""
        You are an agent responsible for obtaining the user's shipping address.

    %s

        When asked to complete a task, follow these instructions:
        1. Present the default shipping address to the user:
           "Your default shipping address is: 123 Main St, San Francisco, CA 94105"
        2. Ask the user: "Would you like to use this address, or would you like to change it?"
        3. Proceed based on the user's response:

        If the user wants to use the default address:
        1. Confirm: "Great! I'll use 123 Main St, San Francisco, CA 94105 as your shipping address."
        2. Call the `get_default_shipping_address` tool to get the default address.
        3. Transfer back to the root_agent with the default shipping address.

        If the user wants to change the address:
        1. Ask: "Please provide your new shipping address. I need the complete address including street, city, state, and ZIP code."
        2. Collect the user's new shipping address. Ensure you have collected all
           of the necessary parts of a US address.
        3. Confirm the new address with the user.
        4. Transfer back to the root_agent with the new shipping address.
    """ % DEBUG_MODE_INSTRUCTIONS,
    tools=[
        tools.get_shipping_address,
        tools.get_default_shipping_address,
    ],
)

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

"""Tools used by the BuyWhenReady collector subagent.

Each agent uses individual tools to handle distinct tasks throughout the
BuyWhenReady condition collection process.
"""

from google.adk.tools.tool_context import ToolContext


def store_buywhenready_conditions(
    conditions: dict,
    tool_context: ToolContext,
) -> str:
    """Stores the user's BuyWhenReady conditions in the tool context.

    Args:
        conditions: Dictionary containing the user's BuyWhenReady conditions
        tool_context: The ADK supplied tool context.

    Returns:
        Confirmation message that conditions were stored.
    """
    tool_context.state["buywhenready_conditions"] = conditions
    return f"BuyWhenReady conditions stored successfully: {conditions}"

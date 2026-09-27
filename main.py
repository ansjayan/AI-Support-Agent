"""
Customer Support AI Agent — Starter Code
==========================================
Your task is to complete this file by implementing all sections marked
with # TODO comments.

Reference the step-by-step solution files and INSTRUCTIONS.md for guidance.
Do NOT copy the solution directly — work through each section yourself.

Run locally (after filling in config values):
  uv run main.py '{"prompt": "Hello", "customer_id": "CUST-123", "session_id": "s1"}'

Deploy to AgentCore:
  agentcore deploy

Invoke deployed agent:
  agentcore invoke '{"prompt": "Hello", "customer_id": "CUST-123", "session_id": "s1"}'
"""

# ── Imports ───────────────────────────────────────────────────────────────────
# These imports are provided. Do not remove them.
from strands import Agent, tool
from bedrock_agentcore.runtime import BedrockAgentCoreApp
from bedrock_agentcore.memory import MemoryClient
from strands.models import BedrockModel
from strands.tools.mcp.mcp_client import MCPClient
from mcp.client.streamable_http import streamable_http_client
import argparse, json
import os, asyncio, boto3
from strands.hooks import (
    HookProvider, AfterInvocationEvent, HookRegistry, MessageAddedEvent,
)
import os

import logging
import uuid
from typing import Dict
from bedrock_agentcore.tools.code_interpreter_client import code_session
from strands_tools.browser import AgentCoreBrowser


logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)
logger = logging.getLogger("CSAI_Agent")

# ── TODO 1 — App Initialisation ───────────────────────────────────────────────
# Create a BedrockAgentCoreApp instance.
# This registers the ASGI server for AgentCore deployment.
# There must be exactly one instance per deployment.
#
# Hint: app = BedrockAgentCoreApp()


# TODO: Create the BedrockAgentCoreApp instance
# app = None  # Replace this line
app = BedrockAgentCoreApp()

# Suppress interactive tool-consent prompts (required in headless deployments).
os.environ["BYPASS_TOOL_CONSENT"] = "true"


# ── TODO 2 — Configuration ────────────────────────────────────────────────────
# Replace the placeholder strings with your actual AWS resource values.
# You collected these in Part 1 of the INSTRUCTIONS.
#
# GATEWAY_URL format: https://<alias>.gateway.bedrock-agentcore.<region>.amazonaws.com/mcp
# KB_ID       format: 10-character alphanumeric string from the KB console
# REGION:     your AWS region, e.g. "us-east-1"
# MEMORY_ID   format: shown in the AgentCore Memory console

# GATEWAY_URL = "<gateway_url>"   # TODO: Replace with your Gateway URL
# KB_ID       = "<kbid>"          # TODO: Replace with your Knowledge Base ID
# REGION      = "<region>"        # TODO: Replace with your AWS region
# MEMORY_ID   = "<mem_id>"        # TODO: Replace with your Memory ID


GATEWAY_URL = "https://customersupportgateway-8niacvdgcn.gateway.bedrock-agentcore.us-east-1.amazonaws.com/mcp"
KB_ID = "CF9FOLQFLO"  # Created near the end to minimize OpenSearch Serverless cost
REGION = "us-east-1"
MEMORY_ID = "CustomerSupportMemory-Z26oG28suK"

# ── TODO 3 — Model and Clients ────────────────────────────────────────────────
# Create:
#   1. A BedrockModel using model_id "global.amazon.nova-2-lite-v1:0"
#   2. A MemoryClient with region_name=REGION
#   3. A boto3 client for the "bedrock-agent-runtime" service in REGION
#
# Hint: model = BedrockModel(model_id=model_id)

model_id = "global.amazon.nova-2-lite-v1:0"

# # TODO: Create the BedrockModel instance
# model = None  # Replace this line

# # TODO: Create the MemoryClient instance
# memory_client = None  # Replace this line

# # TODO: Create the boto3 bedrock-agent-runtime client
# _bedrock_runtime = None  # Replace this line


model = BedrockModel(
    model_id=model_id,
    region_name=REGION,
)

memory_client = MemoryClient(region_name=REGION)

_bedrock_runtime = boto3.client(
    "bedrock-agent-runtime",
    region_name=REGION,
)



# ── TODO 4 — Namespace Helper ─────────────────────────────────────────────────
# Implement get_namespaces() to return a dict mapping strategy type to
# namespace template string.
#
# Steps:
#   1. Call mem_client.get_memory_strategies(memory_id) to get strategy list
#   2. Return a dict: { strategy["type"]: strategy["namespaces"][0] for each strategy }
#
# Example output:
#   { "SEMANTIC": "cs_agent/{actorId}/facts",
#     "USER_PREFERENCE": "cs_agent/{actorId}/preferences" }

# def get_namespaces(mem_client: MemoryClient, memory_id: str) -> Dict:
#     """Return a dict mapping strategy type → namespace template string."""
#     # TODO: Implement this function
#     pass


def get_namespaces(mem_client: MemoryClient, memory_id: str) -> Dict:
    """Return a dict mapping strategy type → namespace template string."""
    strategies = mem_client.get_memory_strategies(memory_id)

    namespaces = {}

    for strategy in strategies:
        strategy_type = strategy.get("type")

        # Current AgentCore uses namespaceTemplates.
        # namespaces is retained for compatibility with older responses.
        templates = (
            strategy.get("namespaceTemplates")
            or strategy.get("namespaces")
            or []
        )

        if strategy_type and templates:
            namespaces[strategy_type] = templates[0]

    return namespaces



# ── TODO 5 — Memory Hook ──────────────────────────────────────────────────────
# Implement MemoryHook, a HookProvider subclass that adds long-term memory.
#
# The class needs:
#   __init__(self, actor_id, session_id, memory_client, memory_id)
#     — store all four as instance attributes
#     — call get_namespaces() and store the result as self.namespaces
#
#   retrieve_customer_context(self, event: MessageAddedEvent)
#     — only runs for plain-text user messages (not tool results)
#     — for each strategy namespace, call memory_client.retrieve_memories(
#          memory_id, namespace (formatted with actorId), query, top_k=5)
#     — collect non-empty memory texts tagged with their strategy type
#     — if any memories found, prepend them to the user message as:
#          "Customer Context:\n<memories>\n\n<original_message>"
#
#   save_support_interaction(self, event: AfterInvocationEvent)
#     — walk the message list backwards to find the last plain-text user
#       query and the last assistant response
#     — call memory_client.create_event(memory_id, actor_id, session_id,
#          messages=[(customer_query, "USER"), (agent_response, "ASSISTANT")])
#
#   register_hooks(self, registry: HookRegistry)
#     — register retrieve_customer_context on MessageAddedEvent
#     — register save_support_interaction on AfterInvocationEvent


# class MemoryHook(HookProvider):
#     """Long-term memory hook for the customer support agent."""

#     def __init__(
#         self,
#         actor_id: str,
#         session_id: str,
#         memory_client: MemoryClient,
#         memory_id: str,
#     ):
#         # TODO: Store actor_id, session_id, memory_id, memory_client as attributes
#         # TODO: Call get_namespaces() and store the result as self.namespaces
#         pass

#     def retrieve_customer_context(self, event: MessageAddedEvent):
#         """Retrieve relevant memories and prepend them to the user message."""
#         # TODO: Implement memory retrieval
#         # Steps:
#         #   1. Get the last message from event.agent.messages
#         #   2. Check it is a user message and not a tool result
#         #   3. Extract the user query text
#         #   4. For each namespace in self.namespaces, call retrieve_memories()
#         #   5. Collect non-empty memory texts with strategy type tags
#         #   6. If any found, prepend them to the user message
#         pass

#     def save_support_interaction(self, event: AfterInvocationEvent):
#         """Save the completed turn to memory after the agent responds."""
#         # TODO: Implement memory saving
#         # Steps:
#         #   1. Get messages from event.agent.messages
#         #   2. Walk backwards to find the last user query (plain text)
#         #      and the last assistant response
#         #   3. Call memory_client.create_event() with both messages
#         pass

#     def register_hooks(self, registry: HookRegistry) -> None:  # type: ignore
#         """Register both memory callbacks."""
#         # TODO: Register retrieve_customer_context on MessageAddedEvent
#         # TODO: Register save_support_interaction on AfterInvocationEvent
#         pass

class MemoryHook(HookProvider):
    """Long-term memory hook for the customer support agent."""

    def __init__(
        self,
        actor_id: str,
        session_id: str,
        memory_client: MemoryClient,
        memory_id: str,
    ):
        self.actor_id = actor_id
        self.session_id = session_id
        self.memory_client = memory_client
        self.memory_id = memory_id
        self.namespaces = get_namespaces(memory_client, memory_id)

    def retrieve_customer_context(self, event: MessageAddedEvent):
        """Retrieve relevant memories and prepend them to the user message."""
        messages = event.agent.messages

        if not messages:
            return

        message = messages[-1]

        # Only process user messages.
        if message.get("role") != "user":
            return

        content = message.get("content", [])

        # Ignore tool-result messages.
        if not content or not isinstance(content, list):
            return

        text_blocks = [
            block.get("text")
            for block in content
            if isinstance(block, dict) and block.get("text")
        ]

        if not text_blocks:
            return

        query = "\n".join(text_blocks)
        memories = []

        for strategy_type, namespace_template in self.namespaces.items():
            namespace = namespace_template.format(actorId=self.actor_id)

            try:
                results = self.memory_client.retrieve_memories(
                    memory_id=self.memory_id,
                    namespace=namespace,
                    query=query,
                    top_k=5,
                )

                for memory in results or []:
                    memory_text = (
                        memory.get("content", {}).get("text")
                        if isinstance(memory.get("content"), dict)
                        else memory.get("content")
                    )

                    if not memory_text:
                        memory_text = memory.get("text")

                    if memory_text:
                        memories.append(
                            f"[{strategy_type}] {memory_text}"
                        )

            except Exception as exc:
                logger.warning(
                    "Memory retrieval failed for %s: %s",
                    strategy_type,
                    exc,
                )

        if memories:
            context_text = "\n".join(memories)

            original_text = content[0].get("text", "")

            content[0]["text"] = (
                f"Customer Context:\n{context_text}\n\n"
                f"{original_text}"
            )

    def save_support_interaction(self, event: AfterInvocationEvent):
        """Save the completed turn to memory after the agent responds."""
        messages = event.agent.messages

        customer_query = None
        agent_response = None

        for message in reversed(messages):
            role = message.get("role")
            content = message.get("content", [])

            if not isinstance(content, list):
                continue

            text_parts = [
                block.get("text")
                for block in content
                if isinstance(block, dict) and block.get("text")
            ]

            if not text_parts:
                continue

            text = "\n".join(text_parts)

            if role == "assistant" and agent_response is None:
                agent_response = text

            elif role == "user" and customer_query is None:
                # Do not save the injected memory context itself.
                if text.startswith("Customer Context:"):
                    parts = text.split("\n\n", 1)
                    if len(parts) == 2:
                        text = parts[1]

                customer_query = text

            if customer_query and agent_response:
                break

        if not customer_query or not agent_response:
            return

        try:
            self.memory_client.create_event(
                memory_id=self.memory_id,
                actor_id=self.actor_id,
                session_id=self.session_id,
                messages=[
                    (customer_query, "USER"),
                    (agent_response, "ASSISTANT"),
                ],
            )

        except Exception as exc:
            logger.warning("Memory save failed: %s", exc)

    def register_hooks(self, registry: HookRegistry) -> None:  # type: ignore
        """Register both memory callbacks."""
        registry.add_callback(
            MessageAddedEvent,
            self.retrieve_customer_context,
        )

        registry.add_callback(
            AfterInvocationEvent,
            self.save_support_interaction,
        )


# ── TODO 6 — Knowledge Base Tool ─────────────────────────────────────────────
# Implement search_knowledge_base(query) using the @tool decorator.
#
# Steps:
#   1. Guard: if KB_ID is empty return "Knowledge base not configured."
#   2. Call _bedrock_runtime.retrieve(
#          knowledgeBaseId=KB_ID,
#          retrievalQuery={"text": query}
#      )
#   3. Extract resp["retrievalResults"]; return a message if empty
#   4. Join the text chunks with "\n---\n" and return the result
#
# The docstring is the tool description — the model uses it to decide when
# to call this tool, so keep it clear and accurate.

@tool
def search_knowledge_base(query: str) -> str:
    """
    Search the Amazon product catalog and support knowledge base.
    Use this for product specifications, return policies, warranty
    information, loyalty program details, and order status definitions.

    Args:
        query: The question or topic to search for

    Returns:
        Relevant information retrieved from the knowledge base
    """
    # # TODO: Implement the Knowledge Base search
    # pass


    if not KB_ID or KB_ID.startswith("<"):
        return "Knowledge base not configured."

    try:
        response = _bedrock_runtime.retrieve(
            knowledgeBaseId=KB_ID,
            retrievalQuery={"text": query},
        )

        results = response.get("retrievalResults", [])

        if not results:
            return "No relevant information found in the knowledge base."

        chunks = []

        for result in results:
            text = result.get("content", {}).get("text")

            if text:
                chunks.append(text)

        if not chunks:
            return "No relevant information found in the knowledge base."

        return "\n---\n".join(chunks)

    except Exception as exc:
        logger.warning("Knowledge base retrieval failed: %s", exc)
        return f"Knowledge base search unavailable: {exc}"

    

# ── TODO 7 — Loyalty Discount Tool (Code Interpreter) ────────────────────────
# Implement calculate_loyalty_discount() using the @tool decorator.
#
# The tool must:
#   1. Build a self-contained Python code string that:
#        • Defines earn_rates: {"standard": 1, "device": 2, "fresh": 5}
#        • Defines tier_rates: {"Silver": 0.00, "Gold": 0.10, "Platinum": 0.15}
#        • Calculates points_redeemed (floor to nearest 500, cap at 50% of order)
#        • Calculates tier_discount (applied to subtotal after points)
#        • Calculates final_total, total_savings, points_earned, remaining_points
#        • Prints a JSON result dict
#   2. Execute the code with code_session(REGION).invoke("executeCode", {...})
#      using language="python" and clearContext=True
#   3. Return the first result event as a JSON string
#   4. Include a fallback that computes only the tier discount if the
#      Code Interpreter is unavailable


# @tool
# def calculate_loyalty_discount(
#     loyalty_points: int,
#     tier: str,
#     order_total: float,
#     product_category: str = "standard",
# ) -> str:
#     """
#     Calculate the loyalty discount for a customer order using the
#     AgentCore Code Interpreter. Runs exact arithmetic in a secure sandbox.

#     Args:
#         loyalty_points:   Customer's current points balance
#         tier:             Customer tier — Silver, Gold, or Platinum
#         order_total:      Order total in USD
#         product_category: standard, device, or fresh

#     Returns:
#         Full discount breakdown and final price
#     """
#     # TODO: Build the code string (use an f-string to inject the arguments)
#     code = ""  # Replace with your code string

#     try:
#         # TODO: Execute the code using code_session and return the result
#         pass

#     except Exception as e:
#         # TODO: Implement fallback calculation using tier discount only
#         pass


@tool
def calculate_loyalty_discount(
    loyalty_points: int,
    tier: str,
    order_total: float,
    product_category: str = "standard",
) -> str:
    """
    Calculate the loyalty discount for a customer order using the
    AgentCore Code Interpreter. Runs exact arithmetic in a secure sandbox.

    Args:
        loyalty_points: Customer's current points balance
        tier: Customer tier — Silver, Gold, or Platinum
        order_total: Order total in USD
        product_category: standard, device, or fresh

    Returns:
        Full discount breakdown and final price
    """

    code = f"""
import json
import math

loyalty_points = {int(loyalty_points)}
tier = {tier!r}
order_total = {float(order_total)}
product_category = {product_category!r}

earn_rates = {{
    "standard": 1,
    "device": 2,
    "fresh": 5
}}

tier_rates = {{
    "Silver": 0.00,
    "Gold": 0.10,
    "Platinum": 0.15
}}

# Points can only be redeemed in blocks of 500.
available_blocks = loyalty_points // 500
available_redeemable_points = available_blocks * 500

# 100 points = $1. Redemption cannot exceed 50% of order value.
max_redemption_dollars = order_total * 0.50
max_points_for_order = math.floor(
    max_redemption_dollars * 100 / 500
) * 500

points_redeemed = min(
    available_redeemable_points,
    max_points_for_order
)

points_discount = points_redeemed / 100.0

subtotal_after_points = max(
    0.0,
    order_total - points_discount
)

tier_rate = tier_rates.get(tier, 0.0)
tier_discount = subtotal_after_points * tier_rate

final_total = max(
    0.0,
    subtotal_after_points - tier_discount
)

total_savings = order_total - final_total

earn_rate = earn_rates.get(product_category.lower(), 1)
points_earned = math.floor(final_total * earn_rate)

remaining_points = (
    loyalty_points
    - points_redeemed
    + points_earned
)

result = {{
    "loyalty_points": loyalty_points,
    "tier": tier,
    "order_total": round(order_total, 2),
    "product_category": product_category,
    "points_redeemed": points_redeemed,
    "points_discount": round(points_discount, 2),
    "tier_discount_pct": round(tier_rate * 100, 2),
    "tier_discount": round(tier_discount, 2),
    "total_savings": round(total_savings, 2),
    "final_total": round(final_total, 2),
    "points_earned": points_earned,
    "remaining_points": remaining_points
}}

print(json.dumps(result))
"""

    try:
        with code_session(REGION) as session:
            response = session.invoke(
                "executeCode",
                {
                    "code": code,
                    "language": "python",
                    "clearContext": True,
                },
            )

            for event in response.get("stream", []):
                result = event.get("result")

                if result is not None:
                    return json.dumps(result)

            return json.dumps({
                "error": "Code Interpreter returned no result."
            })

    except Exception as exc:
        logger.warning(
            "Code Interpreter unavailable; using fallback: %s",
            exc,
        )

        tier_rates = {
            "Silver": 0.00,
            "Gold": 0.10,
            "Platinum": 0.15,
        }

        tier_rate = tier_rates.get(tier, 0.0)
        tier_discount = float(order_total) * tier_rate
        final_total = float(order_total) - tier_discount

        return json.dumps({
            "fallback": True,
            "reason": str(exc),
            "loyalty_points": loyalty_points,
            "tier": tier,
            "order_total": round(float(order_total), 2),
            "points_redeemed": 0,
            "tier_discount_pct": round(tier_rate * 100, 2),
            "tier_discount": round(tier_discount, 2),
            "final_total": round(final_total, 2),
            "remaining_points": loyalty_points,
        })

    

# ── TODO 8 — Agent Entrypoint ─────────────────────────────────────────────────
# Implement the invoke() function decorated with @app.entrypoint.
#
# Steps:
#   1. Extract user_input, actor_id, and session_id from the payload
#      (generate a UUID if session_id is missing)
#   2. Instantiate MemoryHook for this actor/session
#   3. Instantiate AgentCoreBrowser(region=REGION)
#   4. Build the tools list: [search_knowledge_base, calculate_loyalty_discount,
#                              agent_core_browser.browser]
#   5. Connect to the Gateway via MCPClient, load gateway_tools, extend tools list
#   6. Create and invoke the Agent with all tools, hooks, and system_prompt
#   7. Return the text from the first content block of the response
#   8. Handle exceptions gracefully

# @app.entrypoint
# async def invoke(payload, context=None):
#     """
#     Main handler called by AgentCore for every incoming request.

#     Expected payload keys:
#       prompt      (str, required) — the customer's message
#       customer_id (str, optional) — unique customer identifier
#       session_id  (str, optional) — session identifier; generated if absent
#     """
#     # TODO: Implement the agent invocation
#     pass


@app.entrypoint
async def invoke(payload, context=None):
    """
    Main handler called by AgentCore for every incoming request.

    Expected payload keys:
      prompt      (str, required) — the customer's message
      customer_id (str, optional) — unique customer identifier
      session_id  (str, optional) — session identifier; generated if absent
    """

    user_input = payload.get("prompt", "").strip()

    if not user_input:
        return "Please provide a customer support question."

    actor_id = payload.get("customer_id", "anonymous")
    session_id = payload.get("session_id") or str(uuid.uuid4())

    try:
        # Long-term customer memory.
        memory_hook = MemoryHook(
            actor_id=actor_id,
            session_id=session_id,
            memory_client=memory_client,
            memory_id=MEMORY_ID,
        )

        # Managed AgentCore Browser.


        agent_core_browser = AgentCoreBrowser(region=REGION)

        tools = [
            search_knowledge_base,
            calculate_loyalty_discount,
            agent_core_browser.browser,
        ]

        system_prompt = """
You are a helpful customer support AI agent.

Use the available tools whenever they provide authoritative information
instead of inventing customer, order, refund, product, loyalty, or policy
details.

Tool guidance:
- Use OrderAPITarget tools for customer and order information.
- Use RefundTarget tools for refunds, refund status, and return labels.
- Use search_knowledge_base for product information, return policies,
  warranty information, loyalty benefits, and support policies.
- Use calculate_loyalty_discount for loyalty points, tier discounts,
  redemption calculations, and final order totals.
- Use the browser tool when current information from a live website is
  requested.
- Use remembered customer context when relevant, but prioritize the
  customer's current request.

LOYALTY CALCULATION WORKFLOW — REQUIRED:
For EVERY request involving loyalty points, point redemption, tier discounts,
purchase totals, points earned, or remaining points:

1. ALWAYS call calculate_loyalty_discount.
2. NEVER calculate any loyalty value yourself.
3. The calculate_loyalty_discount result is the ONLY source of numerical
   loyalty values.
4. Copy ALL numerical values directly from the tool result.
5. NEVER recompute a percentage, discount, total, points balance, or points
   earned, even if you think a tool value is incorrect.
6. Report tier discounts and percentage values exactly as returned by the tool.
   Do not independently apply the percentage to any subtotal or order total.
7. Do not add explanatory arithmetic that was not returned by the tool.

REFUND WORKFLOW — REQUIRED:
When a customer requests a refund:
1. ALWAYS call OrderAPITarget___getOrder first using the order ID.
2. Read the exact order total returned by that tool.
3. Then call RefundTarget___initiate_refund.
4. You MUST pass the exact order total as the `amount` argument.
5. Pass the customer's reason as `reason`; if no specific reason is given,
   use "Customer requested refund".
6. Never call initiate_refund without first retrieving the order.
7. In the final response, report the exact amount returned by the refund
   tool.

Give clear, concise customer-facing answers. 

CRITICAL TOOL RESULT RULES:
- Treat values returned by tools as authoritative.
- Copy order IDs, refund IDs, tracking numbers, monetary amounts,
  statuses, dates, carriers, loyalty points, and timelines exactly
  from the tool result.
- Never change, estimate, infer, round away, or invent a monetary amount.
- If a tool returns an amount, explicitly use that exact amount in the answer.
- Never claim a full refund, partial refund, or $0 refund unless the tool
  result explicitly says so.
- Never fabricate tool results.


BROWSER WORKFLOW:
- When asked to inspect a web page, use the browser tool efficiently.
- Navigate to the requested URL, inspect only the information needed,
  and then answer the user.
- Do not repeatedly call the browser after the requested information
  has already been obtained.
- For a page-title request, navigate to the URL, obtain the page title,
  and stop browsing.

  


"""

        # Gateway provides the order and refund MCP tools.
        mcp_client = MCPClient(
            lambda: streamable_http_client(GATEWAY_URL)
        )

        try:
            gateway_tools = await mcp_client.load_tools()
            tools.extend(gateway_tools)

            agent = Agent(
                model=model,
                tools=tools,
                hooks=[memory_hook],
                system_prompt=system_prompt,
            )

            response = await agent.invoke_async(user_input)

        # finally:
        #     mcp_client.stop(None, None, None)
        finally:
            try:
                agent_core_browser.close_platform()
            except Exception as exc:
                logger.warning("Browser platform cleanup failed: %s", exc)

            mcp_client.stop(None, None, None)

            
        # Strands responses normally expose the final message as:
        # response.message["content"][0]["text"]
        if hasattr(response, "message"):
            message = response.message

            if isinstance(message, dict):
                content = message.get("content", [])

                for block in content:
                    if isinstance(block, dict) and block.get("text"):
                        return block["text"]

        # Safe fallback for SDK response variations.
        return str(response)

    except Exception as exc:
        logger.exception("Agent invocation failed")
        return f"Unable to process the support request: {exc}"

    

# ── CLI entry point (do not modify) ──────────────────────────────────────────
def main():
    """Run one invocation from the command line for local testing."""
    parser = argparse.ArgumentParser()
    parser.add_argument("payload", type=str)
    args = parser.parse_args()
    response = asyncio.run(invoke(json.loads(args.payload)))
    print(response)


if __name__ == "__main__":
    app.run()
    # Uncomment the line below and comment app.run() for local CLI testing:
    # main()

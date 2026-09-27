import asyncio

from strands.tools.mcp.mcp_client import MCPClient
from mcp.client.streamable_http import streamable_http_client

GATEWAY_URL = "https://customersupportgateway-8niacvdgcn.gateway.bedrock-agentcore.us-east-1.amazonaws.com/mcp"

async def main():
    client = MCPClient(
        lambda: streamable_http_client(GATEWAY_URL)
    )

    try:
        tools = await client.load_tools()

        for tool in tools:
            print("\n==============================")
            print("NAME:", getattr(tool, "tool_name", getattr(tool, "name", None)))
            print("TYPE:", type(tool))
            print("DICT:", getattr(tool, "__dict__", {}))

    finally:
        client.stop(None, None, None)

asyncio.run(main())

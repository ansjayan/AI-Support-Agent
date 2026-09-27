import asyncio

from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client


GATEWAY_URL = "https://customersupportgateway-8niacvdgcn.gateway.bedrock-agentcore.us-east-1.amazonaws.com/mcp"


async def main():
    async with streamable_http_client(GATEWAY_URL) as (
        read_stream,
        write_stream,
    ):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()

            result = await session.list_tools()

            print("\n=== MCP TOOLS ===")
            for tool in result.tools:
                print(tool.name)
            print("\n=== TEST getOrder ===")

            order_result = await session.call_tool(
                "OrderAPITarget___getOrder",
                arguments={
                    "order_id": "ORD-001"
                },
            )

            print(order_result)


            print("\n=== TEST initiate_refund ===")

            refund_result = await session.call_tool(
                "RefundTarget___initiate_refund",
                arguments={
                    "order_id": "ORD-002",
                    "amount": 139.99,
                    "reason": "Customer requested return",
                },
            )

            print(refund_result)            

asyncio.run(main())

"""
LangGraph Agent SDK.

Quick Start:
    from agent import AgentClient
    
    # Sync client
    client = AgentClient(base_url="http://localhost:8000")
    response = client.chat(message="查询销售额")
    print(response.content)
    
    # Async client
    import asyncio
    from agent import AsyncAgentClient
    
    async def main():
        async with AsyncAgentClient() as client:
            response = await client.chat(message="分析数据")
            print(response.content)
    
    asyncio.run(main())

For more: see sdk/agent.py
"""
from sdk.agent import AgentClient, AsyncAgentClient, ChatResponse, create_client

__version__ = "0.2.0"

__all__ = [
    "AgentClient",
    "AsyncAgentClient",
    "ChatResponse", 
    "create_client",
]

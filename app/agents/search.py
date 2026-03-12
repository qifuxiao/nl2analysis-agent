"""
Web Search Agent - searches the web for current information.
"""
import json
import logging
from typing import Dict, Any, List, Optional
from langgraph.prebuilt import create_react_agent

from app.graph.state import AgentExecutionState
from app.llm.client import LLMClient
from app.tools.definitions import search_tools
from app.core.config import settings

logger = logging.getLogger(__name__)

# System prompt for Search Agent
SEARCH_SYSTEM_PROMPT = """你是一个网络搜索助手。你的任务是帮助用户搜索互联网上的最新信息。

## 工作流程：

1. **理解搜索需求** - 理解用户想要搜索什么信息
2. **执行搜索** - 使用 web_search 工具搜索
3. **整理结果** - 整理搜索结果，以清晰的格式返回给用户
4. **提供摘要** - 如果需要，基于搜索结果提供总结

## 可用工具：

- web_search: 搜索互联网
  - 参数：query (搜索关键词), max_results (最大结果数，默认5)
  - 返回：搜索结果列表（标题、URL、内容摘要）

## 搜索技巧：

- 使用简洁的关键词
- 可以指定时间范围（如 "最新", "2024"）
- 可以指定来源（如 "新闻", "博客"）

## 输出格式：

请以清晰的格式返回搜索结果：
- 标题
- 来源URL
- 关键内容摘要

如果用户的问题可以直接回答，请基于搜索结果提供答案。

请按照工作流程处理用户的搜索请求。
"""


class SearchAgent:
    """
    Web Search Agent - searches the web for information.
    """
    
    def __init__(self, llm: Optional[LLMClient] = None):
        self.llm = llm or LLMClient(temperature=0.7)
        self.tools = search_tools
    
    async def execute(self, message: str, history: list = None) -> str:
        """
        Execute web search.
        
        Args:
            message: User's search request
            history: Conversation history
            
        Returns:
            Search results
        """
        try:
            # Check if search API is configured
            if not settings.TAVILY_API_KEY and not settings.BRAVE_API_KEY:
                return "网络搜索功能未配置。请联系管理员配置 TAVILY_API_KEY 或 BRAVE_API_KEY。"
            
            # Build prompt
            prompt = f"""用户请求：{message}

请搜索相关信息并返回结果。

使用 web_search 工具进行搜索。"""
            
            # Use ReAct agent for search
            agent = create_react_agent(
                self.llm._get_client(),
                tools=self.tools,
                state_modifier=SEARCH_SYSTEM_PROMPT
            )
            
            result = await agent.ainvoke({
                "messages": [{"role": "user", "content": prompt}]
            })
            
            # Extract final response
            messages = result.get("messages", [])
            if messages:
                final_message = messages[-1]
                return final_message.content if hasattr(final_message, 'content') else str(final_message)
            
            return "抱歉，无法完成搜索"
        
        except Exception as e:
            logger.error(f"Search execution failed: {e}")
            return f"搜索失败：{str(e)}"


async def search_agent_node(state: AgentExecutionState) -> AgentExecutionState:
    """
    LangGraph node for Search agent.
    """
    message = state.get("message", "")
    history = state.get("history", [])
    
    agent = SearchAgent()
    result = await agent.execute(message, history)
    
    state["result"] = result
    return state

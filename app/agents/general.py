"""
General Chat Agent - handles general conversations using LLM's knowledge.

This is the fallback agent when no specific agent matches the user's intent.
"""
import logging
from typing import Dict, Any, List, Optional
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage

from app.graph.state import AgentExecutionState, AgentType
from app.llm.client import LLMClient
from app.memory.backend import get_memory
from app.core.config import settings

logger = logging.getLogger(__name__)

# System prompt for General Chat Agent
GENERAL_CHAT_SYSTEM_PROMPT = """你是一个专业、友好的AI助手。你可以用中文或英文与用户交流。

## 能力：

- 回答各种问题
- 提供解释和分析
- 帮助解决问题
- 讨论各种话题
- 编写代码和文档

## 风格：

- 回答要准确、有帮助
- 保持友好和专业的语气
- 如果不确定某事，诚实地说明
- 适当使用格式化使回答更清晰

## 对话上下文：

你可以看到之前的对话历史，请利用这些信息提供更相关的回答。

请用中文回答（除非用户使用英文提问）。
"""


class GeneralChatAgent:
    """
    General Chat Agent - handles general conversations.
    
    This is the fallback agent that uses the LLM's general knowledge
    when no specific agent matches the user's intent.
    """
    
    def __init__(self, llm: Optional[LLMClient] = None):
        self.llm = llm or LLMClient(temperature=0.7)
        self.memory = get_memory()
    
    async def execute(
        self,
        message: str,
        user_id: str = "",
        session_id: str = "",
        history: List[Dict] = None,
    ) -> str:
        """
        Execute general chat.
        
        Args:
            message: User's message
            user_id: User identifier (for memory)
            session_id: Session identifier (for memory)
            history: Conversation history
            
        Returns:
            Chat response
        """
        try:
            # Build message history for LLM
            messages = []
            
            # Add system prompt
            messages.append(SystemMessage(content=GENERAL_CHAT_SYSTEM_PROMPT))
            
            # Add conversation history
            if history:
                for msg in history[-10:]:  # Last 10 messages
                    role = msg.get("role", "user")
                    content = msg.get("content", "")
                    if role == "user":
                        messages.append(HumanMessage(content=content))
                    else:
                        messages.append(AIMessage(content=content))
            
            # Add current message
            messages.append(HumanMessage(content=message))
            
            # Get response
            response = await self.llm.ainvoke(messages)
            
            # Save to memory
            if user_id and session_id:
                from app.memory.backend import ChatMessage
                self.memory.save(user_id, session_id, ChatMessage(
                    role="user",
                    content=message,
                ))
                self.memory.save(user_id, session_id, ChatMessage(
                    role="assistant",
                    content=response,
                    agent_type=AgentType.GENERAL.value,
                ))
            
            return response
        
        except Exception as e:
            logger.error(f"General chat failed: {e}")
            return f"抱歉，出了点问题：{str(e)}"
    
    async def stream(
        self,
        message: str,
        user_id: str = "",
        session_id: str = "",
        history: List[Dict] = None,
    ):
        """
        Stream general chat response.
        
        Args:
            message: User's message
            user_id: User identifier (for memory)
            session_id: Session identifier (for memory)
            history: Conversation history
            
        Yields:
            Response chunks
        """
        try:
            # Build message history for LLM
            messages = []
            
            # Add system prompt
            messages.append(SystemMessage(content=GENERAL_CHAT_SYSTEM_PROMPT))
            
            # Add conversation history
            if history:
                for msg in history[-10:]:
                    role = msg.get("role", "user")
                    content = msg.get("content", "")
                    if role == "user":
                        messages.append(HumanMessage(content=content))
                    else:
                        messages.append(AIMessage(content=content))
            
            # Add current message
            messages.append(HumanMessage(content=message))
            
            # Stream response
            collected = ""
            async for chunk in self.llm.astream(messages):
                collected += chunk
                yield chunk
            
            # Save to memory after streaming completes
            if user_id and session_id:
                from app.memory.backend import ChatMessage
                self.memory.save(user_id, session_id, ChatMessage(
                    role="user",
                    content=message,
                ))
                self.memory.save(user_id, session_id, ChatMessage(
                    role="assistant",
                    content=collected,
                    agent_type=AgentType.GENERAL.value,
                ))
        
        except Exception as e:
            logger.error(f"General chat stream failed: {e"抱歉，出了点问题：{}")
            yield fstr(e)}"


async def general_agent_node(state: AgentExecutionState) -> AgentExecutionState:
    """
    LangGraph node for General Chat agent.
    """
    message = state.get("message", "")
    history = state.get("history", [])
    user_id = state.get("user_id", "")
    session_id = state.get("session_id", "")
    
    agent = GeneralChatAgent()
    result = await agent.execute(message, user_id, session_id, history)
    
    state["result"] = result
    return state

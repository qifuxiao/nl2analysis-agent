"""
File Processing Agent - handles file operations.
"""
import json
import logging
from typing import Dict, Any, Optional
from langgraph.prebuilt import create_react_agent

from app.graph.state import AgentExecutionState
from app.llm.client import LLMClient
from app.tools.definitions import file_tools
from app.core.config import settings

logger = logging.getLogger(__name__)

# System prompt for File Agent
FILE_SYSTEM_PROMPT = """你是一个文件处理助手。你的任务是帮助用户读取、写入和管理文件。

## 工作流程：

1. **理解需求** - 理解用户想要对文件做什么操作
2. **执行操作** - 使用适当的工具完成文件操作
3. **返回结果** - 告知用户操作结果

## 可用工具：

- read_file: 读取文件内容
  - 参数：file_path (文件路径), encoding (编码，默认utf-8)
  
- write_file: 写入文件内容
  - 参数：file_path (文件路径), content (内容), encoding (编码)
  
- list_files: 列出目录中的文件
  - 参数：directory (目录), pattern (匹配模式，默认*)

## 安全规则：

- 不允许访问敏感路径（如 /etc/, /root/.ssh/ 等）
- 不允许读取系统配置文件
- 文件操作有大小限制（最大100KB读取）

请按照工作流程处理用户的文件操作请求。
"""


class FileAgent:
    """
    File Processing Agent - handles file operations.
    """
    
    def __init__(self, llm: Optional[LLMClient] = None):
        self.llm = llm or LLMClient(temperature=0.3)
        self.tools = file_tools
    
    async def execute(self, message: str, history: list = None) -> str:
        """
        Execute file operation.
        
        Args:
            message: User's file operation request
            history: Conversation history
            
        Returns:
            Operation result
        """
        try:
            # Build prompt
            prompt = f"""用户请求：{message}

请理解用户的文件操作需求并使用适当的工具执行。

常见的文件操作包括：
- 读取文件：使用 read_file 工具
- 写入文件：使用 write_file 工具
- 列出文件：使用 list_files 工具

请直接执行操作并返回结果。"""
            
            # Use ReAct agent for file operations
            agent = create_react_agent(
                self.llm._get_client(),
                tools=self.tools,
                state_modifier=FILE_SYSTEM_PROMPT
            )
            
            result = await agent.ainvoke({
                "messages": [{"role": "user", "content": prompt}]
            })
            
            # Extract final response
            messages = result.get("messages", [])
            if messages:
                final_message = messages[-1]
                return final_message.content if hasattr(final_message, 'content') else str(final_message)
            
            return "抱歉，无法完成文件操作"
        
        except Exception as e:
            logger.error(f"File operation failed: {e}")
            return f"文件操作失败：{str(e)}"


async def file_agent_node(state: AgentExecutionState) -> AgentExecutionState:
    """
    LangGraph node for File agent.
    """
    message = state.get("message", "")
    history = state.get("history", [])
    
    agent = FileAgent()
    result = await agent.execute(message, history)
    
    state["result"] = result
    return state

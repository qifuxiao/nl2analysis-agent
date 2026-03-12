"""
NL2SQL Agent - converts natural language to SQL queries and executes them.
"""
import json
import logging
from typing import Dict, Any, Optional
from langchain_core.tools import tool
from langgraph.prebuilt import create_react_agent

from app.graph.state import AgentExecutionState, AgentType
from app.llm.client import LLMClient
from app.tools.definitions import get_table_schema, execute_sql, db_tools
from app.core.config import settings

logger = logging.getLogger(__name__)

# System prompt for NL2SQL Agent
NL2SQL_SYSTEM_PROMPT = """你是一个专业的NL2SQL助手。你的任务是将用户的自然语言问题转换为SQL查询，并执行它们获取结果。

## 工作流程：

1. **理解用户问题** - 理解用户想要查询什么数据
2. **获取表结构** - 使用 get_table_schema 工具了解数据库表结构
3. **生成SQL** - 将自然语言转换为SQL查询
4. **执行SQL** - 使用 execute_sql 工具执行查询
5. **返回结果** - 将查询结果以友好的方式返回给用户

## 重要规则：

- 只生成 SELECT 查询，不要生成 INSERT、UPDATE、DELETE
- 表名和列名使用实际数据库中的名称
- 注意数据类型的正确使用
- 如果查询出错，尝试修复并重试
- 返回结果要清晰易懂，必要时可以格式化

## 可用工具：

- get_table_schema: 获取数据库表结构
- execute_sql: 执行SQL查询

请按照工作流程处理用户的查询请求。
"""


class NL2SQLAgent:
    """
    NL2SQL Agent - converts natural language to SQL.
    """
    
    def __init__(self, llm: Optional[LLMClient] = None):
        self.llm = llm or LLMClient(temperature=0.3)
        self.tools = db_tools
    
    async def execute(self, message: str, history: list = None) -> str:
        """
        Execute NL2SQL workflow.
        
        Args:
            message: User's natural language query
            history: Conversation history
            
        Returns:
            Query results as string
        """
        try:
            # Step 1: Get table schema
            schema = get_table_schema.invoke({})
            schema_str = schema if isinstance(schema, str) else str(schema)
            
            # Step 2: Build prompt for SQL generation
            prompt = f"""用户问题：{message}

数据库表结构：
{schema_str}

请将用户问题转换为SQL查询，并执行获取结果。

步骤：
1. 先使用 get_table_schema 确认表结构（如果还没确认）
2. 使用 execute_sql 执行查询
3. 返回结果

注意：只生成 SELECT 查询！"""
            
            # Step 3: Use ReAct agent for SQL generation and execution
            agent = create_react_agent(
                self.llm._get_client(),
                tools=self.tools,
                state_modifier=NL2SQL_SYSTEM_PROMPT
            )
            
            result = await agent.ainvoke({
                "messages": [{"role": "user", "content": prompt}]
            })
            
            # Extract final response
            messages = result.get("messages", [])
            if messages:
                final_message = messages[-1]
                return final_message.content if hasattr(final_message, 'content') else str(final_message)
            
            return "抱歉，无法完成查询"
        
        except Exception as e:
            logger.error(f"NL2SQL execution failed: {e}")
            return f"查询失败：{str(e)}"


async def nl2sql_agent_node(state: AgentExecutionState) -> AgentExecutionState:
    """
    LangGraph node for NL2SQL agent.
    """
    message = state.get("message", "")
    history = state.get("history", [])
    
    agent = NL2SQLAgent()
    result = await agent.execute(message, history)
    
    state["result"] = result
    return state

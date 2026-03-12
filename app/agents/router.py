"""
Intent Router Agent - analyzes user intent and routes to appropriate agent.

This is the core of the multi-agent system, using LLM to understand user intent
and route requests to specialized agents.
"""
import json
import logging
from typing import Optional, Dict, Any
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.tools import BaseTool

from app.graph.state import AgentType, IntentResult, RouterState
from app.llm.client import LLMClient
from app.core.config import settings

logger = logging.getLogger(__name__)

# Intent patterns for rule-based fallback
INTENT_PATTERNS = {
    AgentType.NL2SQL: [
        "查询", "多少", "统计", "select", "sql", "数据库", "表",
        "有多少", "总数", "求和", "平均", "最大", "最小",
        "sales", "users", "orders", "revenue", "count", "sum"
    ],
    AgentType.ANALYSIS: [
        "分析", "趋势", "对比", "图表", "可视化", "报告",
        "增长", "下降", "占比", "分布", "分析一下",
        "analysis", "trend", "chart", "compare", "report"
    ],
    AgentType.FILE: [
        "读取", "写入", "保存", "上传", "下载", "文件",
        "打开", "创建", "删除", "复制", "移动",
        "read", "write", "file", "download", "upload"
    ],
    AgentType.SEARCH: [
        "搜索", "查找", "最新", "新闻", "信息",
        "关于", "是什么", "如何", "怎么",
        "search", "find", "news", "latest", "what is", "how to"
    ],
}

# System prompt for intent router
ROUTER_SYSTEM_PROMPT = """你是一个智能意图路由器。你的任务分析用户的输入，确定用户想要什么类型的帮助，并将请求路由到正确的专业Agent。

## 可用的Agent类型：

1. **nl2sql** (NL2SQL Agent) - 当用户想要查询数据库、获取统计数据时
   - 关键词：查询数据库、统计数量、求和、平均、最大、最小、SQL查询
   
2. **analysis** (数据分析 Agent) - 当用户想要分析数据、生成图表、获取洞察时
   - 关键词：分析数据、趋势分析、对比、图表、可视化、报告

3. **file** (文件处理 Agent) - 当用户想要读取、写入、操作文件时
   - 关键词：读取文件、写入文件、上传、下载、文件操作

4. **search** (网络搜索 Agent) - 当用户想要获取最新信息、搜索互联网时
   - 关键词：搜索、查找最新、新闻、实时信息

5. **general** (通用聊天 Agent) - 当问题不属于以上任何类别，使用大模型通用知识回答
   - 日常对话、闲聊、通用知识问题

## 输出格式：

请以JSON格式返回分析结果，不要包含其他内容：

```json
{
  "agent_type": "nl2sql|analysis|file|search|general",
  "confidence": 0.95,
  "reasoning": "简短说明为什么选择这个Agent",
  "extracted_params": {
    // 从用户输入中提取的关键参数
  }
}
```

confidence 范围 0-1，表示你对判断的自信程度。
"""


class IntentRouter:
    """
    Intent Router - analyzes user messages and routes to appropriate agents.
    
    Uses both rule-based pattern matching and LLM-based classification
    for robust intent detection.
    """
    
    def __init__(self, llm: Optional[LLMClient] = None):
        self.llm = llm or LLMClient(temperature=0.3)
    
    def _rule_based_detect(self, message: str) -> Optional[IntentResult]:
        """
        Rule-based intent detection using keyword patterns.
        
        This provides a fast fallback when LLM is unavailable.
        """
        message_lower = message.lower()
        
        scores = {}
        for agent_type, patterns in INTENT_PATTERNS.items():
            score = sum(1 for p in patterns if p.lower() in message_lower)
            if score > 0:
                scores[agent_type] = score
        
        if not scores:
            return None
        
        # Get the agent with highest score
        best_agent = max(scores, key=scores.get)
        confidence = min(scores[best_agent] / len(INTENT_PATTERNS[best_agent]), 1.0)
        
        return IntentResult(
            agent_type=best_agent,
            confidence=confidence,
            reasoning=f"Matched {scores[best_agent]} keyword patterns",
            extracted_params={}
        )
    
    async def detect(
        self,
        message: str,
        history: list = None,
        user_id: str = "",
    ) -> IntentResult:
        """
        Detect user intent from message.
        
        Args:
            message: User's input message
            history: Conversation history (optional)
            user_id: User identifier (optional)
            
        Returns:
            IntentResult with agent type and confidence
        """
        # First try rule-based detection for speed
        rule_result = self._rule_based_detect(message)
        if rule_result and rule_result.confidence >= 0.8:
            logger.info(f"Rule-based intent detected: {rule_result.agent_type}")
            return rule_result
        
        # Use LLM for more nuanced detection
        try:
            history_text = ""
            if history:
                recent = history[-5:]  # Last 5 messages
                history_text = "\n".join([
                    f"{m.get('role', 'user')}: {m.get('content', '')}"
                    for m in recent
                ])
            
            prompt = f"""分析以下用户输入，确定用户意图：

当前用户输入：{message}

历史对话：
{history_text}

请返回JSON格式的意图分析结果："""

            response = await self.llm.ainvoke(
                message=prompt,
                system_prompt=ROUTER_SYSTEM_PROMPT
            )
            
            # Parse JSON response
            try:
                # Try to extract JSON from response
                if "```json" in response:
                    response = response.split("```json")[1].split("```")[0]
                elif "```" in response:
                    response = response.split("```")[1].split("```")[0]
                
                result = json.loads(response.strip())
                
                # Validate and normalize
                agent_type = result.get("agent_type", "general").lower()
                if agent_type not in [e.value for e in AgentType]:
                    agent_type = "general"
                
                return IntentResult(
                    agent_type=AgentType(agent_type),
                    confidence=float(result.get("confidence", 0.7)),
                    reasoning=result.get("reasoning", ""),
                    extracted_params=result.get("extracted_params", {})
                )
            
            except (json.JSONDecodeError, KeyError) as e:
                logger.warning(f"Failed to parse LLM intent response: {e}")
                # Fallback to rule-based or default to general
                return rule_result or IntentResult(
                    agent_type=AgentType.GENERAL,
                    confidence=0.5,
                    reasoning="LLM解析失败，使用默认处理",
                    extracted_params={}
                )
        
        except Exception as e:
            logger.error(f"Intent detection failed: {e}")
            # Fallback to rule-based
            return rule_result or IntentResult(
                agent_type=AgentType.GENERAL,
                confidence=0.5,
                reasoning="意图检测异常，使用通用处理",
                extracted_params={}
            )


async def router_node(state: RouterState) -> RouterState:
    """
    LangGraph node for intent routing.
    
    This node analyzes the user's message and determines which
    agent should handle the request.
    """
    message = state.get("message", "")
    history = state.get("history", [])
    user_id = state.get("user_id", "")
    
    if not message:
        state["intent"] = IntentResult(
            agent_type=AgentType.GENERAL,
            confidence=0.0,
            reasoning="Empty message",
            extracted_params={}
        )
        state["selected_agent"] = AgentType.GENERAL
        return state
    
    router = IntentRouter()
    intent = await router.detect(message, history, user_id)
    
    state["intent"] = intent
    state["selected_agent"] = intent.agent_type
    
    logger.info(f"Routed to {intent.agent_type} (confidence: {intent.confidence})")
    
    return state


def should_route_to_agent(state: RouterState) -> str:
    """
    Conditional routing function.
    
    Determines which branch to take in the LangGraph.
    """
    agent = state.get("selected_agent", AgentType.GENERAL)
    
    if agent == AgentType.NL2SQL:
        return "nl2sql"
    elif agent == AgentType.ANALYSIS:
        return "analysis"
    elif agent == AgentType.FILE:
        return "file"
    elif agent == AgentType.SEARCH:
        return "search"
    else:
        return "general"

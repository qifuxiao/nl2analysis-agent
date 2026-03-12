"""
Data Analysis Agent - analyzes data and generates visualizations.
"""
import json
import logging
from typing import Dict, Any, Optional, List
from langgraph.prebuilt import create_react_agent

from app.graph.state import AgentExecutionState
from app.llm.client import LLMClient
from app.tools.definitions import analyze_data, generate_chart_config, analysis_tools
from app.core.config import settings

logger = logging.getLogger(__name__)

# System prompt for Analysis Agent
ANALYSIS_SYSTEM_PROMPT = """你是一个专业的数据分析师助手。你的任务是帮助用户分析数据、生成洞察和可视化。

## 工作流程：

1. **理解需求** - 理解用户想要分析什么数据
2. **数据处理** - 如果需要，使用 analyze_data 工具进行分析
3. **生成图表** - 使用 generate_chart_config 生成图表配置
4. **提供洞察** - 基于分析结果提供见解和建议

## 可用工具：

- analyze_data: 分析数据类型
  - summary: 数据摘要（行数、列数、类型、统计信息）
  - trends: 趋势分析（均值、标准差）
  - correlations: 相关性分析
  - outliers: 异常值检测
  
- generate_chart_config: 生成图表配置
  - bar: 柱状图
  - line: 折线图
  - pie: 饼图
  - scatter: 散点图

## 输出要求：

- 分析结果要清晰易懂
- 图表配置返回JSON格式，可在Chart.js中使用
- 提供有价值的业务洞察

请按照工作流程处理用户的数据分析请求。
"""


class AnalysisAgent:
    """
    Data Analysis Agent - analyzes data and generates visualizations.
    """
    
    def __init__(self, llm: Optional[LLMClient] = None):
        self.llm = llm or LLMClient(temperature=0.7)
        self.tools = analysis_tools
    
    async def execute(
        self,
        message: str,
        data: Optional[str] = None,
        history: List[Dict] = None,
    ) -> Dict[str, Any]:
        """
        Execute analysis workflow.
        
        Args:
            message: User's analysis request
            data: Optional data in JSON format
            history: Conversation history
            
        Returns:
            Analysis results including text and chart config
        """
        try:
            # Build prompt
            if data:
                prompt = f"""用户请求：{message}

数据：
{data}

请分析数据并提供：
1. 数据摘要和统计信息
2. 趋势或模式分析
3. 建议的图表类型和配置

使用 analyze_data 和 generate_chart_config 工具。"""
            else:
                prompt = f"""用户请求：{message}

请帮助用户进行数据分析。如果需要用户提供数据，请明确说明。

可以使用以下分析类型：
- summary: 数据摘要
- trends: 趋势分析
- correlations: 相关性分析
- outliers: 异常值检测"""
            
            # Use ReAct agent for analysis
            agent = create_react_agent(
                self.llm._get_client(),
                tools=self.tools,
                state_modifier=ANALYSIS_SYSTEM_PROMPT
            )
            
            result = await agent.ainvoke({
                "messages": [{"role": "user", "content": prompt}]
            })
            
            # Extract final response
            messages = result.get("messages", [])
            if messages:
                final_message = messages[-1]
                response_text = final_message.content if hasattr(final_message, 'content') else str(final_message)
                
                # Try to extract chart config if present
                chart_config = None
                try:
                    if "```json" in response_text:
                        json_parts = response_text.split("```json")
                        for part in json_parts[1:]:
                            chart_config = json.loads(part.split("```")[0])
                            break
                except:
                    pass
                
                return {
                    "analysis": response_text,
                    "chart_config": chart_config,
                }
            
            return {
                "analysis": "抱歉，无法完成分析",
                "chart_config": None,
            }
        
        except Exception as e:
            logger.error(f"Analysis execution failed: {e}")
            return {
                "analysis": f"分析失败：{str(e)}",
                "chart_config": None,
            }


async def analysis_agent_node(state: AgentExecutionState) -> AgentExecutionState:
    """
    LangGraph node for Analysis agent.
    """
    message = state.get("message", "")
    history = state.get("history", [])
    intent = state.get("intent", {})
    
    # Extract data from intent params if provided
    data = intent.get("extracted_params", {}).get("data")
    
    agent = AnalysisAgent()
    result = await agent.execute(message, data, history)
    
    state["result"] = result.get("analysis", "")
    state["visualization_config"] = result.get("chart_config")
    return state

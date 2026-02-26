'''
Author: qifuxiao 867225266@qq.com
Date: 2026-02-14 02:15:10
LastEditors: Please set LastEditors
LastEditTime: 2026-02-26 11:19:04
FilePath: /nl2analysis-agent/app/graph/graph.py
Description: 这是默认设置,请设置`customMade`, 打开koroFileHeader查看配置 进行设置: https://github.com/OBKoro1/koro1FileHeader/wiki/%E9%85%8D%E7%BD%AE
'''
# app/agent/graph.py
from app.core.logger import logger
from langgraph.graph import StateGraph
from app.graph.state import GraphState
from app.graph.nodes import (
    pre_memory_node,
    time_prompt_node,
    analysis_prompt_node,
    alert_rule_node,
    feature_engineering_node,
    risk_scoring_node
)

graph = StateGraph(GraphState)

graph.add_node("pre_memory", pre_memory_node)
logger.info("Added node: pre_memory_node")
logger.info(f"Current nodes: {graph.nodes}")
graph.add_node("time_prompt", time_prompt_node)
graph.add_node("alert_rule", alert_rule_node)
graph.add_node("analysis_prompt", analysis_prompt_node)
graph.add_node("feature_engineering", feature_engineering_node)
graph.add_node("risk_scoring", risk_scoring_node)


graph.set_entry_point("pre_memory")

graph.add_edge("pre_memory", "time_prompt")
graph.add_edge("time_prompt", "alert_rule")
graph.add_edge("alert_rule_node", "feature_engineering")
graph.add_edge("feature_engineering", "risk_scoring")
graph.add_edge("risk_scoring", "llm_analysis")




app_graph = graph.compile(
    debug=True,  # ✅ 打印执行轨迹到 stdout
    checkpointer=None  # 临时禁用 checkpointer 简化调试
)

'''
Author: qifuxiao 867225266@qq.com
Date: 2026-02-14 02:15:10
FilePath: /alexqi/develop/nl2analysis-agent/app/agent/graph.py
'''
from langgraph.graph import StateGraph
from app.agent.state import AgentState
from app.agent.nodes import (
    pre_memory_node, nl2sql_node, db_query_node,
    analysis_node, chart_node, clarification_node, post_memory_node
)

graph = StateGraph(AgentState)

graph.add_node("pre_memory", pre_memory_node)
graph.add_node("nl2sql", nl2sql_node)
graph.add_node("query_db", db_query_node)
graph.add_node("analysis", analysis_node)
# graph.add_node("chart", chart_node)
graph.add_node("clarify", clarification_node)
graph.add_node("post_memory", post_memory_node)

graph.set_entry_point("pre_memory")
graph.add_edge("pre_memory", "nl2sql")
graph.add_edge("nl2sql", "query_db")

def router(state):
    return "clarify" if state.get("error") else "analysis"

graph.add_conditional_edges("query_db", router, {"clarify": "clarify", "analysis": "analysis"})
# graph.add_edge("analysis", "chart")
# graph.add_edge("chart", "post_memory")
graph.add_edge("clarify", "nl2sql")

app_graph = graph.compile()

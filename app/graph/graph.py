'''
Author: qifuxiao 867225266@qq.com
Date: 2026-02-14 02:15:10
LastEditors: qifuxiao 867225266@qq.com
LastEditTime: 2026-02-17 02:51:11
FilePath: /nl2analysis-agent/app/graph/graph.py
Description: 这是默认设置,请设置`customMade`, 打开koroFileHeader查看配置 进行设置: https://github.com/OBKoro1/koro1FileHeader/wiki/%E9%85%8D%E7%BD%AE
'''
# app/agent/graph.py

from langgraph.graph import StateGraph
from app.graph.state import GraphState
from app.graph.nodes import (
    pre_memory_node,
    nl2sql_node,
    db_query_node,
    analysis_node,
)

graph = StateGraph(GraphState)

graph.add_node("pre_memory", pre_memory_node)
graph.add_node("nl2sql", nl2sql_node)
graph.add_node("query_db", db_query_node)
graph.add_node("analysis", analysis_node)

graph.set_entry_point("pre_memory")

graph.add_edge("pre_memory", "nl2sql")
graph.add_edge("nl2sql", "query_db")
graph.add_edge("query_db", "analysis")

app_graph = graph.compile()

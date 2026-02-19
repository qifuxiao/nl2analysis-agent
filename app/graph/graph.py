'''
Author: qifuxiao 867225266@qq.com
Date: 2026-02-14 02:15:10
LastEditors: qifuxiao 867225266@qq.com
LastEditTime: 2026-02-18 00:45:25
FilePath: /nl2analysis-agent/app/graph/graph.py
Description: 这是默认设置,请设置`customMade`, 打开koroFileHeader查看配置 进行设置: https://github.com/OBKoro1/koro1FileHeader/wiki/%E9%85%8D%E7%BD%AE
'''
# app/agent/graph.py

from langgraph.graph import StateGraph
from app.graph.state import GraphState
from app.graph.nodes import (
    pre_memory_node,
    db_query_node,
    nl2sql_prompt_node,
    sql_llm_node,
    analysis_prompt_node
)

graph = StateGraph(GraphState)

graph.add_node("pre_memory", pre_memory_node)

graph.add_node("nl2sql_prompt", nl2sql_prompt_node)
graph.add_node("sql_llm", sql_llm_node)

graph.add_node("db_query", db_query_node)

graph.add_node("analysis_prompt", analysis_prompt_node)




graph.set_entry_point("pre_memory")

graph.add_edge("pre_memory", "nl2sql_prompt")
graph.add_edge("nl2sql_prompt", "sql_llm")
graph.add_edge("sql_llm", "db_query")
graph.add_edge("db_query", "analysis_prompt")




app_graph = graph.compile()

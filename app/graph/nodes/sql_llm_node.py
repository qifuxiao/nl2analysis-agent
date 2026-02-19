'''
Author: qifuxiao 867225266@qq.com
Date: 2026-02-17 13:41:35
LastEditors: qifuxiao 867225266@qq.com
LastEditTime: 2026-02-18 00:34:17
FilePath: /nl2analysis-agent/app/graph/nodes/sql_llm_node.py
Description: 这是默认设置,请设置`customMade`, 打开koroFileHeader查看配置 进行设置: https://github.com/OBKoro1/koro1FileHeader/wiki/%E9%85%8D%E7%BD%AE
'''
from app.llm.client import get_llm
from app.utils.db_tool import extract_pure_sql
from app.memory.models import ChatMessage
from app.core.logger import logger
llm = get_llm()

async def sql_llm_node(state):
    raw_sql_msg = await llm.ainvoke(state["sql_prompt"])
    raw_sql = raw_sql_msg.content  # 注意这里
    clean_sql = extract_pure_sql(raw_sql)
#     state.setdefault("history", [])
#     logger.info(f"{type(clean_sql)=}")
#     state["history"].append(ChatMessage(
#     type="AIMessage",
#     content=clean_sql,
#     additional_kwargs=getattr(clean_sql, "additional_kwargs", {})
# ))
    return {"sql": clean_sql}

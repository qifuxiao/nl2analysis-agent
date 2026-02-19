'''
Author: qifuxiao 867225266@qq.com
Date: 2026-02-17 02:21:48
LastEditors: qifuxiao 867225266@qq.com
LastEditTime: 2026-02-18 00:33:42
FilePath: /nl2analysis-agent/app/graph/nodes/db_query_node.py
Description: 这是默认设置,请设置`customMade`, 打开koroFileHeader查看配置 进行设置: https://github.com/OBKoro1/koro1FileHeader/wiki/%E9%85%8D%E7%BD%AE
'''
import asyncio
from app.utils.db_tool import run_sql
from app.core.logger import logger
from app.memory.models import ChatMessage
async def db_query_node(state):
    try:
        # 使用 run_in_executor 避免 SQL 查询阻塞事件循环
        loop = asyncio.get_event_loop()
        logger.info(f"state['sql']")
        data = await loop.run_in_executor(None, run_sql, state["sql"])
        if not data:
#             state.setdefault("history", [])
#             state["history"].append(ChatMessage(
#     type="AIMessage",
#     content="查询结果为空"
# ))
            return {"error": "查询结果为空", "raw_data": []}
#         state.setdefault("history", [])
        logger.info(f"{type(data)=}")
#         state["history"].append(ChatMessage(
#     type="AIMessage",
#     content=data,
#     additional_kwargs=getattr(data, "additional_kwargs", {})
# ))
        return {"raw_data": data}
    except Exception as e:
        return {"error": str(e)}
'''
Author: qifuxiao 867225266@qq.com
Date: 2026-02-17 02:21:48
LastEditors: qifuxiao 867225266@qq.com
LastEditTime: 2026-02-17 02:44:57
FilePath: /nl2analysis-agent/app/graph/nodes/db_query_node.py
Description: 这是默认设置,请设置`customMade`, 打开koroFileHeader查看配置 进行设置: https://github.com/OBKoro1/koro1FileHeader/wiki/%E9%85%8D%E7%BD%AE
'''
import asyncio
from app.utils.db_tool import run_sql
async def db_query_node(state):
    try:
        # 使用 run_in_executor 避免 SQL 查询阻塞事件循环
        loop = asyncio.get_event_loop()
        data = await loop.run_in_executor(None, run_sql, state["sql"])
        if not data:
            return {"error": "查询结果为空", "raw_data": []}
        return {"raw_data": data}
    except Exception as e:
        return {"error": str(e)}
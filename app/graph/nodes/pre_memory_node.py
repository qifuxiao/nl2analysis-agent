'''
Author: qifuxiao 867225266@qq.com
Date: 2026-02-17 02:17:07
LastEditors: qifuxiao 867225266@qq.com
LastEditTime: 2026-02-17 02:19:46
FilePath: /nl2analysis-agent/app/graph/nodes/pre_memory_node.py
Description: 这是默认设置,请设置`customMade`, 打开koroFileHeader查看配置 进行设置: https://github.com/OBKoro1/koro1FileHeader/wiki/%E9%85%8D%E7%BD%AE
'''
from app.memory.backend import load_session

import asyncio

async def pre_memory_node(state):
    # 异步包装同步 IO
    loop = asyncio.get_event_loop()
    memory = await loop.run_in_executor(None, load_session, state["user_id"], state["session_id"])
    return {"history": [m.__dict__ for m in memory.messages]}
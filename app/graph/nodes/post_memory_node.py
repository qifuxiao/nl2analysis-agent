'''
Author: qifuxiao 867225266@qq.com
Date: 2026-02-17 02:24:37
LastEditors: qifuxiao 867225266@qq.com
LastEditTime: 2026-02-17 02:24:50
FilePath: /nl2analysis-agent/app/graph/nodes/post_memory_node.py
Description: 这是默认设置,请设置`customMade`, 打开koroFileHeader查看配置 进行设置: https://github.com/OBKoro1/koro1FileHeader/wiki/%E9%85%8D%E7%BD%AE
'''

from app.memory.backend import load_session, save_session

from app.memory.models import ChatMessage

import asyncio


async def post_memory_node(state):
    loop = asyncio.get_event_loop()
    def _save():
        memory = load_session(state["user_id"], state["session_id"])
        memory.messages.append(ChatMessage(role="user", content=state["query"]))
        memory.messages.append(ChatMessage(role="assistant", content=state["analysis"].get("summary", "")))
        save_session(memory)
    await loop.run_in_executor(None, _save)
    return {}
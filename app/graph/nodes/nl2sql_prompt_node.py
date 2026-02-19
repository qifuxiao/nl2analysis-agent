'''
Author: qifuxiao 867225266@qq.com
Date: 2026-02-17 13:41:07
LastEditors: qifuxiao 867225266@qq.com
LastEditTime: 2026-02-17 15:28:54
FilePath: /nl2analysis-agent/app/graph/nodes/nl2sql_prompt_node.py
Description: 这是默认设置,请设置`customMade`, 打开koroFileHeader查看配置 进行设置: https://github.com/OBKoro1/koro1FileHeader/wiki/%E9%85%8D%E7%BD%AE
'''
from app.core.schema_index import schema_index
from app.memory.models import ChatMessage
from app.core.logger import logger
async def nl2sql_prompt_node(state):
    tables = schema_index.retrieve(state["query"], k=5)
    tables_schema = "\n".join(tables)

    prompt = (
        "你是一个专业的 SQL 生成专家。\n"
        "请根据表结构生成 SELECT 语句。\n"
        "严禁 Markdown 标签。\n\n"
        f"【表结构】\n{tables_schema}\n\n"
        f"【问题】{state['query']}"
    )
#     state.setdefault("history", [])
#     logger.info(f"{type(prompt)=}")
#     state["history"].append(ChatMessage(
#     type="AIMessage",
#     content=prompt,
#     additional_kwargs=getattr(prompt, "additional_kwargs", {})
# ))
    return {"sql_prompt": prompt}

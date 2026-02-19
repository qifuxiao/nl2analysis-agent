'''
Author: qifuxiao 867225266@qq.com
Date: 2026-02-17 02:06:54
LastEditors: qifuxiao 867225266@qq.com
LastEditTime: 2026-02-18 00:33:19
FilePath: /nl2analysis-agent/app/graph/nodes/analysis.py
Description: 这是默认设置,请设置`customMade`, 打开koroFileHeader查看配置 进行设置: https://github.com/OBKoro1/koro1FileHeader/wiki/%E9%85%8D%E7%BD%AE
'''
# app/graph/nodes/analysis.py

from app.graph.state import GraphState
import pandas as pd
from app.llm.client import get_llm
from app.memory.models import ChatMessage
from app.core.logger import logger
llm = get_llm()
async def analysis_node(state: GraphState):
    raw_data = state.get("raw_data")

    if not raw_data:
        state.setdefault("history", [])
        state["history"].append(ChatMessage(
    type="AIMessage",
    content="未查询到数据"
    
))
        return {"analysis": "未查询到数据。"}

    df = pd.DataFrame(raw_data)
    stats = df.describe(include="all").to_dict()

    prompt = (
        f"用户问题：{state['query']}\n"
        f"统计信息：{stats}\n"
        "请输出中文业务结论，并给出1-2条运营建议。"
    )

    result_text = await llm.ainvoke(prompt)
    # state.setdefault("history", [])
    logger.info(f"{type(result_text)=}")
#     state["history"].append(ChatMessage(
#     type="AIMessage",
#     content=result_text,
#     additional_kwargs=getattr(result_text, "additional_kwargs", {})
# ))
    return {
        "analysis": result_text
    }


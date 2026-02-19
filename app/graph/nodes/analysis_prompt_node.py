'''
Author: qifuxiao 867225266@qq.com
Date: 2026-02-17 13:41:57
LastEditors: qifuxiao 867225266@qq.com
LastEditTime: 2026-02-18 00:33:27
FilePath: /nl2analysis-agent/app/graph/nodes/analysis_prompt_node.py
Description: 这是默认设置,请设置`customMade`, 打开koroFileHeader查看配置 进行设置: https://github.com/OBKoro1/koro1FileHeader/wiki/%E9%85%8D%E7%BD%AE
'''
import pandas as pd
from  app.memory.models import ChatMessage
from app.core.logger import logger
async def analysis_prompt_node(state):
    raw_data = state.get("raw_data")

    if not raw_data:
        return {"analysis_prompt": "未查询到数据。"}

    df = pd.DataFrame(raw_data)
    stats = df.describe(include="all").to_dict()

    prompt = (
        f"用户问题：{state['query']}\n"
        f"统计信息：{stats}\n"
        "请输出中文业务结论，并给出1-2条运营建议。"
    )
    # state.setdefault("history", [])
    logger.info(f"{type(prompt)=}")
#     state["history"].append(ChatMessage(
#     type="AIMessage",
#     content=prompt,
#     additional_kwargs=getattr(prompt, "additional_kwargs", {})
# ))
    return {"analysis_prompt": prompt}

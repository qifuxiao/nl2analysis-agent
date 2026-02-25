'''
Author: qifuxiao 867225266@qq.com
Date: 2026-02-17 13:41:57
LastEditors: Please set LastEditors
LastEditTime: 2026-02-25 08:25:48
FilePath: /nl2analysis-agent/app/graph/nodes/analysis_prompt_node.py
Description: 这是默认设置,请设置`customMade`, 打开koroFileHeader查看配置 进行设置: https://github.com/OBKoro1/koro1FileHeader/wiki/%E9%85%8D%E7%BD%AE
'''
import pandas as pd
from  app.memory.models import ChatMessage
from app.core.logger import logger
async def analysis_prompt_node(state):
    raw_data = state.get("alert_rule_data")
    
    if not raw_data:
        return {"analysis_prompt": "未查询到数据。"}

    df = pd.DataFrame(raw_data)
    stats = df.describe(include="all").to_dict()

    prompt = (
        f"用户问题：{state['query']}\n"
        f"统计信息：{stats}\n"
        "请输出中文业务结论，并给出1-2条运营建议。"
    )
    logger.info(f"{type(prompt)=}")
    
    # 🔥 关键：确认执行到 return 前
    logger.info(f"🔹 [BEFORE RETURN] analysis_prompt_node about to return, prompt_len={len(prompt)}")
    
    result = {"analysis_prompt": prompt}
    logger.info(f"🔹 [RETURNING] {result.keys()}")
    return {"analysis_prompt": prompt}

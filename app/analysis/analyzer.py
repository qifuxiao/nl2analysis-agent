'''
Author: qifuxiao 867225266@qq.com
Date: 2026-02-14 02:32:08
LastEditors: qifuxiao 867225266@qq.com
LastEditTime: 2026-02-16 05:42:36
FilePath: /nl2analysis-agent/app/analysis/analyzer.py
Description: 这是默认设置,请设置`customMade`, 打开koroFileHeader查看配置 进行设置: https://github.com/OBKoro1/koro1FileHeader/wiki/%E9%85%8D%E7%BD%AE
'''
import pandas as pd
from app.llm.client import get_llm

llm = get_llm()

async def analyze_data(data: list[dict], query: str) -> dict:
    df = pd.DataFrame(data)
    if df.empty:
        return {"summary": "本次查询无数据。"}

    stats = df.describe(include="all").to_dict()
    prompt = f"用户问题：{query}\n统计信息：{stats}\n请输出中文业务结论，并给出1-2条运营建议。"
    
    # 确保是 ainvoke
    response = await llm.ainvoke(prompt) 
    summary = response.content.strip()
    return {"summary": summary, "stats": stats}
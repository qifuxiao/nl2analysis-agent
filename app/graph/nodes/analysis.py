'''
Author: qifuxiao 867225266@qq.com
Date: 2026-02-17 02:06:54
LastEditors: qifuxiao 867225266@qq.com
LastEditTime: 2026-02-17 02:07:02
FilePath: /nl2analysis-agent/app/graph/nodes/analysis.py
Description: 这是默认设置,请设置`customMade`, 打开koroFileHeader查看配置 进行设置: https://github.com/OBKoro1/koro1FileHeader/wiki/%E9%85%8D%E7%BD%AE
'''
# app/graph/nodes/analysis.py

from app.graph.state import GraphState
import pandas as pd


def analysis_node(state: GraphState):

    raw_data = state.get("raw_data")

    if not raw_data:
        state["analysis_prompt"] = None
        return state

    df = pd.DataFrame(raw_data)
    stats = df.describe(include="all").to_dict()

    prompt = (
        f"用户问题：{state['query']}\n"
        f"统计信息：{stats}\n"
        "请输出中文业务结论，并给出1-2条运营建议。"
    )

    state["analysis_prompt"] = prompt
    return state

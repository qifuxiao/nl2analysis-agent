'''
Author: qifuxiao 867225266@qq.com
Date: 2026-02-14 02:17:48
LastEditors: qifuxiao 867225266@qq.com
LastEditTime: 2026-02-17 13:43:13
FilePath: /nl2analysis-agent/app/graph/state.py
Description: 这是默认设置,请设置`customMade`, 打开koroFileHeader查看配置 进行设置: https://github.com/OBKoro1/koro1FileHeader/wiki/%E9%85%8D%E7%BD%AE
'''
# app/graph/state.py

from typing import TypedDict, List, Dict, Any, Optional


class GraphState(TypedDict):
    user_id: str
    session_id: str
    query: str
    history: list
    sql_prompt: str
    sql: str
    raw_data: list
    analysis_prompt: str
    analysis: str

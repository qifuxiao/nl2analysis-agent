'''
Author: qifuxiao 867225266@qq.com
Date: 2026-02-14 02:17:48
LastEditors: qifuxiao 867225266@qq.com
LastEditTime: 2026-02-17 02:50:31
FilePath: /nl2analysis-agent/app/graph/state.py
Description: 这是默认设置,请设置`customMade`, 打开koroFileHeader查看配置 进行设置: https://github.com/OBKoro1/koro1FileHeader/wiki/%E9%85%8D%E7%BD%AE
'''
# app/graph/state.py

from typing import TypedDict, List, Dict, Any, Optional


class GraphState(TypedDict, total=False):
    """
    NL2Analysis Graph 状态定义

    total=False 表示字段都是可选的
    """

    # =========================
    # 输入层
    # =========================
    query: str
    user_id: str
    session_id: str
    history: List[Dict[str, str]]
    tenant_id: str

    # =========================
    # 中间层
    # =========================
    sql: str
    raw_data: List[Dict[str, Any]]
    analysis_prompt: str

    # =========================
    # 输出层
    # =========================
    final_answer: str

    # =========================
    # 调试信息
    # =========================
    error: Optional[str]
    debug_info: Optional[Dict[str, Any]]

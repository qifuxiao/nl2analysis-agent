'''
Author: qifuxiao 867225266@qq.com
Date: 2026-02-14 02:17:48
LastEditors: Please set LastEditors
LastEditTime: 2026-02-25 08:19:43
FilePath: /nl2analysis-agent/app/graph/state.py
Description: 这是默认设置,请设置`customMade`, 打开koroFileHeader查看配置 进行设置: https://github.com/OBKoro1/koro1FileHeader/wiki/%E9%85%8D%E7%BD%AE
'''
# app/graph/state.py

from typing import TypedDict, List, Dict, Any, Optional


class GraphState(TypedDict):
    user_id: str
    session_id: str
    query: str
    gid: Optional[str]
    start_time: Optional[str]
    end_time: Optional[str]
    alert_rule_data: Optional[Dict[str, Any]]
    alert_rule_query_params: Optional[Dict[str, Any]]
    alert_rule_status: Optional[str]
    history: List[Dict[str, Any]]  # 用于存储对话历史等信息
    analysis_prompt: Optional[str]  # 存储分析提示词

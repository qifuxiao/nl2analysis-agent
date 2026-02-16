'''
Author: qifuxiao 867225266@qq.com
Date: 2026-02-14 02:17:48
FilePath: /alexqi/develop/nl2analysis-agent/app/agent/state.py
'''
# app/agent/state.py
from typing import TypedDict, Optional, List

class AgentState(TypedDict):
    user_id: str
    session_id: str
    query: str
    history: List[dict]
    sql: Optional[str]
    raw_data: Optional[list[dict]]
    analysis: Optional[dict]
    error: Optional[str]

'''
Author: qifuxiao 867225266@qq.com
Date: 2026-02-14 02:17:08
FilePath: /alexqi/develop/nl2analysis-agent/app/memory/models.py
'''
from dataclasses import dataclass, field
from typing import List

@dataclass
class ChatMessage:
    role: str
    content: str

@dataclass
class SessionMemory:
    user_id: str
    session_id: str
    messages: List[ChatMessage] = field(default_factory=list)
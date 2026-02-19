'''
Author: qifuxiao 867225266@qq.com
Date: 2026-02-14 02:17:08
FilePath: /alexqi/develop/nl2analysis-agent/app/memory/models.py
'''
from dataclasses import dataclass, field, asdict
from typing import List
from datetime import date, datetime
@dataclass
class ChatMessage:
    type: str  # "AIMessage" / "UserMessage"
    content: str
    additional_kwargs: dict = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    @staticmethod
    def from_dict(data: dict):
        return ChatMessage(
            type=data.get("type", "AIMessage"),
            content=data.get("content", ""),
            additional_kwargs=data.get("additional_kwargs", {}),
            timestamp=data.get("timestamp", datetime.now().isoformat())
        )

    def to_dict(self):
        return asdict(self)
@dataclass
class SessionMemory:
    user_id: str
    session_id: str
    messages: List[ChatMessage] = field(default_factory=list)

    def to_dict(self):
        return {"messages": [m.to_dict() for m in self.messages]}

    @staticmethod
    def from_dict(user_id: str, session_id: str, data: dict):
        messages = [ChatMessage.from_dict(m) for m in data.get("messages", [])]
        return SessionMemory(user_id=user_id, session_id=session_id, messages=messages)
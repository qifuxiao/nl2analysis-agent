'''
Author: qifuxiao 867225266@qq.com
Date: 2026-02-14 02:14:27
FilePath: /alexqi/develop/nl2analysis-agent/app/memory/backend.py
'''
import json
import redis
from app.memory.models import ChatMessage, SessionMemory
from app.core.config import settings

r = redis.Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, decode_responses=True)

def key(user_id, session_id):
    return f"session:{user_id}:{session_id}"

def load_session(user_id, session_id) -> SessionMemory:
    raw = r.get(key(user_id, session_id))
    if not raw:
        return SessionMemory(user_id=user_id, session_id=session_id)
    data = json.loads(raw)
    return SessionMemory(
        user_id=user_id,
        session_id=session_id,
        messages=[ChatMessage(**m) for m in data["messages"]]
    )

def save_session(memory: SessionMemory):
    r.set(key(memory.user_id, memory.session_id), json.dumps({
        "messages": [m.__dict__ for m in memory.messages]
    }), ex=86400)

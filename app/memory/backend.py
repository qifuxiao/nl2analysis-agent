'''
Author: qifuxiao 867225266@qq.com
Date: 2026-02-14 02:14:27
FilePath: /alexqi/develop/nl2analysis-agent/app/memory/backend.py
'''
import json
import redis
from app.memory.models import ChatMessage, SessionMemory
from app.core.config import settings
from app.core.logger import logger

r = redis.Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, decode_responses=True)

def key(user_id, session_id):
    return f"session:{user_id}:{session_id}"

def load_session(user_id, session_id) -> SessionMemory:
    raw = r.get(key(user_id, session_id))
    if not raw:
        return SessionMemory(user_id=user_id, session_id=session_id)
    data = json.loads(raw)
    return SessionMemory.from_dict(user_id, session_id, data)  # ✅ 使用 from_dict()

def save_session(memory: SessionMemory):
    logger.info(f"{memory=}")
    r.set(
        key(memory.user_id, memory.session_id),
        json.dumps(memory.to_dict()),  # ✅ 使用 to_dict()
        ex=86400
    )

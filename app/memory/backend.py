'''
Author: qifuxiao 867225266@qq.com
Date: 2026-02-14 02:14:27
FilePath: /nl2analysis-agent/app/memory/backend.py
Description: 测试环境：使用内存缓存替代 Redis（勿用于生产）
'''
import json
import time
from typing import Dict, Optional
from app.memory.models import ChatMessage, SessionMemory
from app.core.config import settings
from app.core.logger import logger
import redis

# 🔥 测试模式开关：根据环境变量或配置决定
USE_REDIS = getattr(settings, "USE_REDIS", True)
print(f"🔧 Memory backend: {'Redis' if USE_REDIS else 'In-Memory Cache'}")
# 🔥 内存缓存存储：{key: {"data": str, "expire_at": float}}
_memory_cache: Dict[str, dict] = {}


def _cache_key(user_id: str, session_id: str) -> str:
    """生成缓存键"""
    return f"session:{user_id}:{session_id}"


def _cleanup_expired():
    """清理过期缓存项（简单惰性清理）"""
    now = time.time()
    expired_keys = [k for k, v in _memory_cache.items() if v["expire_at"] and v["expire_at"] < now]
    for k in expired_keys:
        del _memory_cache[k]
    if expired_keys:
        logger.debug(f"🧹 Cleaned {len(expired_keys)} expired cache items")


if USE_REDIS:
    # 🔥 生产环境：使用 Redis
    logger.info(f"🔌 Connecting to Redis: {settings.REDIS_HOST}:{settings.REDIS_PORT}")
    r = redis.Redis(
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT,
        decode_responses=True,
        socket_connect_timeout=5
    )
    # 测试连接
    try:
        r.ping()
        logger.info("✅ Redis connected successfully")
    except redis.ConnectionError as e:
        logger.warning(f"⚠️ Redis connection failed: {e}. Falling back to memory cache.")
        USE_REDIS = False


def load_session(user_id: str, session_id: str) -> SessionMemory:
    """加载会话：优先 Redis，失败则 fallback 到内存"""
    cache_key = _cache_key(user_id, session_id)
    
    # 🔥 每次检查配置（不修改全局状态）
    use_redis = getattr(settings, "USE_REDIS", True)
    
    if use_redis:
        try:
            raw = r.get(cache_key)
            if not raw:
                return SessionMemory(user_id=user_id, session_id=session_id)
            data = json.loads(raw)
            return SessionMemory.from_dict(user_id, session_id, data)
        except redis.ConnectionError as e:
            # 🔥 仅记录日志，不修改全局变量
            logger.warning(f"⚠️ Redis unavailable: {e}. Using memory cache for this request.")
            # 继续执行内存缓存逻辑（不 return，让代码自然 fallthrough）
    
    # 🔥 内存缓存逻辑（Redis 失败或配置禁用时执行）
    _cleanup_expired()
    item = _memory_cache.get(cache_key)
    if not item:
        return SessionMemory(user_id=user_id, session_id=session_id)
    
    data = json.loads(item["data"])
    return SessionMemory.from_dict(user_id, session_id, data)


def save_session(memory: SessionMemory, ttl_seconds: int = 86400):
    """保存会话：优先 Redis，失败则 fallback 到内存"""
    cache_key = _cache_key(memory.user_id, memory.session_id)
    data_json = json.dumps(memory.to_dict())
    
    # 🔥 每次检查配置
    use_redis = getattr(settings, "USE_REDIS", True)
    
    if use_redis:
        try:
            r.set(cache_key, data_json, ex=ttl_seconds)
            logger.info(f"💾 Saved to Redis: {cache_key}")
            return
        except redis.ConnectionError as e:
            logger.warning(f"⚠️ Redis save failed: {e}. Using memory cache.")
            # 继续执行内存缓存逻辑
    
    # 🔥 内存缓存逻辑
    _memory_cache[cache_key] = {
        "data": data_json,
        "expire_at": time.time() + ttl_seconds if ttl_seconds else None
    }
    logger.info(f"💾 Saved to memory: {cache_key}")
# 🔥 测试专用：清空内存缓存（可选）
def clear_test_cache():
    """仅测试用：清空所有内存缓存"""
    global _memory_cache
    count = len(_memory_cache)
    _memory_cache = {}
    logger.info(f"🗑️  Test cache cleared: {count} items")
    return count
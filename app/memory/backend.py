"""
Memory management for conversation history.
Supports both in-memory and Redis-backed storage.
"""
import json
import logging
import redis
from typing import List, Dict, Any, Optional
from datetime import datetime
from dataclasses import dataclass, field, asdict

from app.core.config import settings

logger = logging.getLogger(__name__)


@dataclass
class ChatMessage:
    """Chat message representation."""
    role: str  # "user" or "assistant"
    content: str
    agent_type: Optional[str] = None  # Which agent handled this
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ChatMessage":
        return cls(**data)


class MemoryBackend:
    """
    Memory backend for storing conversation history.
    
    Supports:
    - Redis (distributed)
    - In-memory (local development)
    """
    
    def __init__(self, use_redis: bool = True):
        self.use_redis = use_redis and settings.REDIS_HOST
        self._redis: Optional[redis.Redis] = None
        
        if self.use_redis:
            try:
                self._redis = redis.Redis(
                    host=settings.REDIS_HOST,
                    port=settings.REDIS_PORT,
                    db=settings.REDIS_DB,
                    password=settings.REDIS_PASSWORD,
                    decode_responses=True,
                )
                self._redis.ping()
                logger.info("Redis memory backend connected")
            except Exception as e:
                logger.warning(f"Redis connection failed: {e}, falling back to in-memory")
                self.use_redis = False
                self._memory: Dict[str, List[Dict]] = {}
        else:
            self._memory: Dict[str, List[Dict]] = {}
            logger.info("In-memory memory backend initialized")
    
    def _get_key(self, user_id: str, session_id: str) -> str:
        """Generate Redis key for session."""
        return f"agent:session:{user_id}:{session_id}"
    
    def load(
        self,
        user_id: str,
        session_id: str,
        limit: int = 50,
    ) -> List[ChatMessage]:
        """
        Load conversation history.
        
        Args:
            user_id: User identifier
            session_id: Session identifier
            limit: Maximum messages to load
            
        Returns:
            List of ChatMessage objects
        """
        key = self._get_key(user_id, session_id)
        
        try:
            if self.use_redis and self._redis:
                data = self._redis.lrange(key, -limit, -1)
                messages = [json.loads(m) for m in data]
                return [ChatMessage.from_dict(m) for m in messages]
            else:
                messages = self._memory.get(key, [])[-limit:]
                return [ChatMessage.from_dict(m) for m in messages]
        except Exception as e:
            logger.error(f"Failed to load memory: {e}")
            return []
    
    def save(
        self,
        user_id: str,
        session_id: str,
        message: ChatMessage,
    ) -> None:
        """
        Save a single message to history.
        
        Args:
            user_id: User identifier
            session_id: Session identifier
            message: Message to save
        """
        key = self._get_key(user_id, session_id)
        data = json.dumps(message.to_dict())
        
        try:
            if self.use_redis and self._redis:
                self._redis.rpush(key, data)
                self._redis.expire(key, settings.REDIS_SESSION_TTL)
                # Trim to limit
                self._redis.ltrim(key, -settings.REDIS_SESSION_TTL, -1)
            else:
                if key not in self._memory:
                    self._memory[key] = []
                self._memory[key].append(message.to_dict())
        except Exception as e:
            logger.error(f"Failed to save memory: {e}")
    
    def save_messages(
        self,
        user_id: str,
        session_id: str,
        messages: List[ChatMessage],
    ) -> None:
        """
        Save multiple messages at once.
        
        Args:
            user_id: User identifier
            session_id: Session identifier
            messages: Messages to save
        """
        for msg in messages:
            self.save(user_id, session_id, msg)
    
    def clear(
        self,
        user_id: str,
        session_id: str,
    ) -> None:
        """
        Clear session history.
        
        Args:
            user_id: User identifier
            session_id: Session identifier
        """
        key = self._get_key(user_id, session_id)
        
        try:
            if self.use_redis and self._redis:
                self._redis.delete(key)
            else:
                self._memory.pop(key, None)
        except Exception as e:
            logger.error(f"Failed to clear memory: {e}")
    
    def get_history_for_llm(
        self,
        user_id: str,
        session_id: str,
        limit: int = 10,
    ) -> List[Dict[str, str]]:
        """
        Get history formatted for LLM consumption.
        
        Args:
            user_id: User identifier
            session_id: Session identifier
            limit: Number of recent messages
            
        Returns:
            List of {"role": ..., "content": ...} dicts
        """
        messages = self.load(user_id, session_id, limit)
        return [{"role": m.role, "content": m.content} for m in messages]


# Global memory instance
memory = MemoryBackend()


def get_memory() -> MemoryBackend:
    """Get the global memory backend instance."""
    return memory

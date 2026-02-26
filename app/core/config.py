'''
Author: qifuxiao 867225266@qq.com
Date: 2026-02-14 02:12:16
FilePath: /nl2analysis-agent/app/core/config.py
'''
import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()

# 🔥 辅助函数：将字符串转换为布尔值
def _str_to_bool(value: str, default: bool) -> bool:
    """转换环境变量字符串为 bool: 'true'/'1'/'yes' → True"""
    if value is None:
        return default
    return str(value).lower().strip() in ("true", "1", "yes", "on")

@dataclass
class Settings:
    
    # 🔥 新增：Redis 开关（默认 True，生产环境启用）
    USE_REDIS: bool = _str_to_bool(os.getenv("USE_REDIS"), True)
    
    REDIS_HOST: str = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT: int = int(os.getenv("REDIS_PORT", "6379"))

    LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "openai")
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    LLM_MODEL: str = os.getenv("LLM_MODEL", "gpt-4.1-mini")
    BASE_URL: str = os.getenv("BASE_URL", "")
    SSO_APP_ID: str = os.getenv("SSO_APP_ID", "")
    SSO_SECRET_KEY: str = os.getenv("SSO_SECRET_KEY", "")
    API_DOMAIN: str = os.getenv("API_DOMAIN", "https://192.168.101.54:8888")
    EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")
    EMBEDDING_BASE_URL: str = os.getenv("EMBEDDING_BASE_URL", "")
    EMBEDDING_API_KEY: str = os.getenv("EMBEDDING_API_KEY", "")

settings = Settings()
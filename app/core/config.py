"""
Core configuration for the multi-agent system.
"""
import os
from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    # App Settings
    APP_NAME: str = "LangGraph Agent"
    APP_VERSION: str = "0.2.0"
    DEBUG: bool = False
    
    # API Settings
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    API_KEY: Optional[str] = Field(default=None, description="API key for authentication")
    
    # LLM Settings
    LLM_PROVIDER: str = "openai"  # openai, deepseek, vllm, anthropic
    OPENAI_API_KEY: str = ""
    ANTHROPIC_API_KEY: str = ""
    LLM_MODEL: str = "gpt-4o-mini"
    LLM_TEMPERATURE: float = 0.7
    LLM_MAX_TOKENS: int = 4096
    BASE_URL: str = ""  # For self-hosted models
    
    # Embedding Settings
    EMBEDDING_PROVIDER: str = "openai"
    EMBEDDING_MODEL: str = "text-embedding-3-small"
    EMBEDDING_API_KEY: str = ""
    EMBEDDING_BASE_URL: str = ""
    
    # Redis Settings (for memory)
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: Optional[str] = None
    REDIS_SESSION_TTL: int = 86400  # 24 hours
    
    # Database Settings (for NL2SQL agent)
    DB_TYPE: str = "postgres"  # postgres, mysql, sqlite
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    DB_NAME: str = "demo"
    DB_USER: str = "demo"
    DB_PASSWORD: str = ""
    
    # Web Search Settings
    BRAVE_API_KEY: str = ""
    TAVILY_API_KEY: str = ""
    
    # File Storage Settings
    UPLOAD_DIR: str = "./uploads"
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    
    # Intent Router Settings
    INTENT_CONFIDENCE_THRESHOLD: float = 0.6
    ENABLE_FALLBACK_TO_GENERAL: bool = True
    
    # Tool Settings
    TOOL_MAX_RETRIES: int = 3
    TOOL_TIMEOUT: int = 30


# Global settings instance
settings = Settings()


# LLM Model Mappings
LLM_MODEL_MAPPING = {
    "gpt-4o": "openai",
    "gpt-4o-mini": "openai",
    "gpt-4-turbo": "openai",
    "deepseek-chat": "deepseek",
    "deepseek-coder": "deepseek",
    "claude-3-5-sonnet": "anthropic",
    "claude-3-haiku": "anthropic",
}


def get_llm_config() -> dict:
    """Get LLM configuration based on provider."""
    provider = settings.LLM_PROVIDER.lower()
    
    if provider == "openai":
        return {
            "model": settings.LLM_MODEL,
            "api_key": settings.OPENAI_API_KEY,
            "base_url": settings.BASE_URL or None,
            "temperature": settings.LLM_TEMPERATURE,
            "max_tokens": settings.LLM_MAX_TOKENS,
        }
    elif provider == "anthropic":
        return {
            "model": settings.LLM_MODEL,
            "api_key": settings.ANTHROPIC_API_KEY,
            "temperature": settings.LLM_TEMPERATURE,
            "max_tokens": settings.LLM_MAX_TOKENS,
        }
    elif provider in ("deepseek", "vllm"):
        return {
            "model": settings.LLM_MODEL,
            "api_key": settings.OPENAI_API_KEY or "dummy-key",
            "base_url": settings.BASE_URL,
            "temperature": settings.LLM_TEMPERATURE,
            "max_tokens": settings.LLM_MAX_TOKENS,
        }
    else:
        raise ValueError(f"Unsupported LLM provider: {provider}")

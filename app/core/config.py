"""
Core configuration for Chat Service.
"""
import os
from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    # OpenAI Configuration
    openai_api_key: str = Field(default="", description="OpenAI API Key")
    openai_base_url: str = Field(
        default="https://api.openai.com/v1",
        description="API base URL"
    )
    default_model: str = Field(default="gpt-4o-mini", description="Default model")
    
    # Generation Parameters
    temperature: float = Field(default=0.7, description="Sampling temperature")
    max_tokens: int = Field(default=4096, description="Max tokens")
    top_p: float = Field(default=1.0, description="Top p sampling")
    
    # Embedding Configuration
    embedding_model: str = Field(
        default="text-embedding-3-small",
        description="Embedding model"
    )
    embedding_dim: int = Field(default=1536, description="Embedding dimension")
    
    # Knowledge Base
    chroma_persist_dir: str = Field(
        default="./data/chroma",
        description="Chroma persist directory"
    )
    chunk_size: int = Field(default=500, description="Chunk size")
    chunk_overlap: int = Field(default=50, description="Chunk overlap")
    
    # Text2SQL
    sql_metadata_path: str = Field(
        default="./data/metadata.sql",
        description="SQL metadata path"
    )
    
    # Server
    host: str = Field(default="0.0.0.0", description="Server host")
    port: int = Field(default=8000, description="Server port")
    debug: bool = Field(default=False, description="Debug mode")


settings = Settings()


# Configured Models
CONFIGURED_MODELS = [
    {
        "id": "gpt-4o-mini",
        "name": "GPT-4o Mini",
        "provider": "openai",
        "max_tokens": 16384,
        "context_window": 128000,
    },
    {
        "id": "gpt-4o",
        "name": "GPT-4o",
        "provider": "openai",
        "max_tokens": 16384,
        "context_window": 128000,
    },
    {
        "id": "gpt-3.5-turbo",
        "name": "GPT-3.5 Turbo",
        "provider": "openai",
        "max_tokens": 4096,
        "context_window": 16385,
    },
]

# Running Models (can be changed at runtime)
running_models = {
    "default": settings.default_model,
    "gpt-4o-mini": True,
    "gpt-4o": False,
    "gpt-3.5-turbo": True,
}

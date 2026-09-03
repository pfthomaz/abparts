"""
Configuration settings for the AI Assistant service.
"""

import os
from typing import List
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Service configuration
    ENVIRONMENT: str = Field(default="development")
    DEBUG: bool = Field(default=True)
    
    # OpenAI configuration
    OPENAI_API_KEY: str = Field(default="")
    OPENAI_MODEL: str = Field(default="gpt-4")
    OPENAI_FALLBACK_MODEL: str = Field(default="gpt-3.5-turbo")
    OPENAI_MAX_TOKENS: int = Field(default=1000)
    OPENAI_TEMPERATURE: float = Field(default=0.7)
    OPENAI_TIMEOUT: int = Field(default=30)
    OPENAI_MAX_RETRIES: int = Field(default=3)

    # Embedding configuration
    # text-embedding-3-small: 1536 dims, cheaper and materially better retrieval
    # quality than the legacy text-embedding-ada-002. If you change the model or
    # dimension you MUST rebuild the vector index (POST /knowledge/reindex).
    OPENAI_EMBEDDING_MODEL: str = Field(default="text-embedding-3-small")
    EMBEDDING_DIMENSION: int = Field(default=1536)

    # Knowledge base / retrieval tuning
    # VECTOR_INDEX_PATH must live on a persistent volume in production, otherwise
    # the FAISS index is wiped on every container recreate and the assistant
    # silently loses all of its knowledge.
    VECTOR_INDEX_PATH: str = Field(default="data/vector_index")
    KB_CHUNK_SIZE: int = Field(default=1100)
    KB_CHUNK_OVERLAP: int = Field(default=300)
    KB_SEARCH_MIN_RELEVANCE: float = Field(default=0.18)
    KB_SEARCH_MAX_CONTEXT_CHUNKS: int = Field(default=14)
    KB_SEARCH_NEIGHBOR_RADIUS: int = Field(default=1)
    KB_QUERY_EXPANSION: bool = Field(default=True)
    KB_EMBED_CONCURRENCY: int = Field(default=6)

    # Database configuration (for session storage)
    DATABASE_URL: str = Field(default="")
    
    # Redis configuration (for session management)
    REDIS_URL: str = Field(default="redis://localhost:6379/0")
    
    # CORS configuration
    CORS_ALLOWED_ORIGINS: str = Field(
        default="http://localhost:3000,http://localhost:3001,http://127.0.0.1:3000,http://127.0.0.1:3001"
    )
    
    # ABParts integration
    ABPARTS_API_URL: str = Field(default="http://api:8000")
    ABPARTS_API_BASE_URL: str = Field(default="http://api:8000/api")
    
    # Security and encryption
    AI_ENCRYPTION_KEY: str = Field(default="")
    
    # Logging configuration
    LOG_LEVEL: str = Field(default="INFO")
    
    model_config = {
        "env_file": ".env",
        "case_sensitive": True,
        "extra": "ignore"  # Ignore extra environment variables
    }
        
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Parse CORS origins from comma-separated string
        self.CORS_ALLOWED_ORIGINS = [
            origin.strip() 
            for origin in self.CORS_ALLOWED_ORIGINS.split(",")
            if origin.strip()  # Filter out empty strings
        ]


# Global settings instance
settings = Settings()
"""
Configuration settings for Janus Prop AI Backend

This module provides centralized configuration management using Pydantic settings.
"""

import os
from typing import List, Optional
from pathlib import Path
from pydantic_settings import BaseSettings
from pydantic import Field, validator

class Settings(BaseSettings):
    """Application settings with environment variable support."""
    
    # Application Configuration
    APP_NAME: str = "Janus Prop AI Backend"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = Field(default=False, env="DEBUG")
    
    # Server Configuration
    HOST: str = Field(default="0.0.0.0", env="HOST")
    PORT: int = Field(default=8000, env="PORT")
    
    # CORS Configuration
    CORS_ORIGINS: List[str] = Field(
        default=[
            "http://localhost:5173",  # Vite default
            "http://localhost:3000",  # React default
            "http://localhost:4173",  # Vite preview
            "http://127.0.0.1:5173",
            "http://127.0.0.1:3000",
            "http://127.0.0.1:4173",
            "http://localhost:8080",  # Alternative port
            "http://127.0.0.1:8080"
        ],
        env="CORS_ORIGINS"
    )
    
    # Database Configuration
    DATABASE_URL: str = Field(
        default="postgresql://user:password@localhost:5432/janus_prop_ai",
        env="DATABASE_URL"
    )
    DATABASE_POOL_SIZE: int = Field(default=10, env="DATABASE_POOL_SIZE")
    DATABASE_MAX_OVERFLOW: int = Field(default=20, env="DATABASE_MAX_OVERFLOW")
    DATABASE_POOL_TIMEOUT: int = Field(default=30, env="DATABASE_POOL_TIMEOUT")
    
    # Supabase Configuration
    SUPABASE_PROJECT_ID: Optional[str] = Field(default=None, env="SUPABASE_PROJECT_ID")
    SUPABASE_SERVICE_ROLE_KEY: Optional[str] = Field(default=None, env="SUPABASE_SERVICE_ROLE_KEY")
    SUPABASE_URL: Optional[str] = Field(default=None, env="SUPABASE_URL")
    SUPABASE_ANON_KEY: Optional[str] = Field(default=None, env="SUPABASE_ANON_KEY")
    
    # Use Supabase if configured, otherwise fall back to local database
    @property
    def is_supabase_enabled(self) -> bool:
        return all([
            self.SUPABASE_PROJECT_ID,
            self.SUPABASE_SERVICE_ROLE_KEY,
            self.SUPABASE_URL,
            self.SUPABASE_ANON_KEY
        ])
    
    @property
    def supabase_database_url(self) -> str:
        """Generate Supabase database URL from components."""
        if not self.is_supabase_enabled:
            raise ValueError("Supabase not properly configured")
        
        # Extract host from SUPABASE_URL (remove https:// and .supabase.co)
        host = self.SUPABASE_URL.replace("https://", "").replace(".supabase.co", "")
        return f"postgresql://postgres.{self.SUPABASE_PROJECT_ID}:{self.SUPABASE_SERVICE_ROLE_KEY}@{host}.supabase.co:5432/postgres"
    
    # Redis Configuration
    REDIS_URL: str = Field(
        default="redis://localhost:6379/0",
        env="REDIS_URL"
    )
    REDIS_PASSWORD: Optional[str] = Field(default=None, env="REDIS_PASSWORD")
    REDIS_DB: int = Field(default=0, env="REDIS_DB")
    REDIS_MAX_CONNECTIONS: int = Field(default=20, env="REDIS_MAX_CONNECTIONS")
    
    # API Keys
    OPENAI_API_KEY: Optional[str] = Field(default=None, env="OPENAI_API_KEY")
    ANTHROPIC_API_KEY: Optional[str] = Field(default=None, env="ANTHROPIC_API_KEY")
    GEMINI_API_KEY: Optional[str] = Field(default=None, env="GEMINI_API_KEY")
    
    # Real Estate API Keys
    ZILLOW_API_KEY: Optional[str] = Field(default=None, env="ZILLOW_API_KEY")
    REDFIN_API_KEY: Optional[str] = Field(default=None, env="REDFIN_API_KEY")
    REALTOR_API_KEY: Optional[str] = Field(default=None, env="REALTOR_API_KEY")
    ATTOM_API_KEY: Optional[str] = Field(default=None, env="ATTOM_API_KEY")
    ESTATED_API_KEY: Optional[str] = Field(default=None, env="ESTATED_API_KEY")
    FRED_API_KEY: Optional[str] = Field(default=None, env="FRED_API_KEY")
    RAPIDAPI_KEY: Optional[str] = Field(default=None, env="RAPIDAPI_KEY")
    API_KEY: Optional[str] = Field(default=None, env="API_KEY")
    
    # LangChain Configuration
    LANGCHAIN_TRACING_V2: bool = Field(default=False, env="LANGCHAIN_TRACING_V2")
    LANGCHAIN_ENDPOINT: Optional[str] = Field(default=None, env="LANGCHAIN_ENDPOINT")
    LANGCHAIN_API_KEY: Optional[str] = Field(default=None, env="LANGCHAIN_API_KEY")
    LANGCHAIN_PROJECT: str = Field(default="janus-prop-ai", env="LANGCHAIN_PROJECT")
    
    # Security Configuration
    SECRET_KEY: str = Field(
        default="your-secret-key-here-change-in-production",
        env="SECRET_KEY"
    )
    ALGORITHM: str = Field(default="HS256", env="ALGORITHM")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30, env="ACCESS_TOKEN_EXPIRE_MINUTES")
    JWT_EXPIRATION_HOURS: int = Field(default=24, env="JWT_EXPIRATION_HOURS")
    PASSWORD_HASH_ROUNDS: int = Field(default=12, env="PASSWORD_HASH_ROUNDS")
    
    # Rate Limiting
    RATE_LIMIT_REQUESTS_PER_MINUTE: int = Field(default=100, env="RATE_LIMIT_REQUESTS_PER_MINUTE")
    RATE_LIMIT_BURST_SIZE: int = Field(default=200, env="RATE_LIMIT_BURST_SIZE")
    
    # Logging Configuration
    LOG_LEVEL: str = Field(default="INFO", env="LOG_LEVEL")
    LOG_FILE: Optional[str] = Field(default=None, env="LOG_FILE")
    LOG_MAX_SIZE: int = Field(default=100, env="LOG_MAX_SIZE")  # MB
    LOG_BACKUP_COUNT: int = Field(default=5, env="LOG_BACKUP_COUNT")
    
    # Agent Configuration
    MAX_CONCURRENT_AGENTS: int = Field(default=10, env="MAX_CONCURRENT_AGENTS")
    MAX_CONCURRENT_AGENT_TASKS: int = Field(default=5, env="MAX_CONCURRENT_AGENT_TASKS")
    AGENT_TIMEOUT: int = Field(default=300, env="AGENT_TIMEOUT")  # seconds
    AGENT_HEARTBEAT_TIMEOUT: int = Field(default=300, env="AGENT_HEARTBEAT_TIMEOUT")
    AGENT_HEALTH_CHECK_INTERVAL: int = Field(default=30, env="AGENT_HEALTH_CHECK_INTERVAL")
    
    # Real-time Configuration
    WEBSOCKET_HEARTBEAT_INTERVAL: int = Field(default=30, env="WEBSOCKET_HEARTBEAT_INTERVAL")
    REALTIME_UPDATE_INTERVAL: int = Field(default=5, env="REALTIME_UPDATE_INTERVAL")  # seconds
    
    # Data Processing
    MAX_PROPERTIES_PER_REQUEST: int = Field(default=1000, env="MAX_PROPERTIES_PER_REQUEST")
    DATA_SYNC_INTERVAL: int = Field(default=300, env="DATA_SYNC_INTERVAL")  # seconds
    CACHE_TTL_SECONDS: int = Field(default=1800, env="CACHE_TTL_SECONDS")
    MAX_PAGE_SIZE: int = Field(default=100, env="MAX_PAGE_SIZE")
    DEFAULT_PAGE_SIZE: int = Field(default=20, env="DEFAULT_PAGE_SIZE")
    
    # File Upload Configuration
    MAX_FILE_SIZE: int = Field(default=50 * 1024 * 1024, env="MAX_FILE_SIZE")  # 50MB
    UPLOAD_DIR: str = Field(default="uploads", env="UPLOAD_DIR")
    
    # Monitoring and Metrics
    ENABLE_METRICS: bool = Field(default=True, env="ENABLE_METRICS")
    METRICS_PORT: int = Field(default=9090, env="METRICS_PORT")
    
    # External Services
    SENTRY_DSN: Optional[str] = Field(default=None, env="SENTRY_DSN")
    
    @validator("CORS_ORIGINS", pre=True)
    def parse_cors_origins(cls, v):
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v
    
    @validator("SECRET_KEY")
    def validate_secret_key(cls, v):
        if v == "your-secret-key-here-change-in-production":
            import secrets
            return secrets.token_urlsafe(32)
        return v
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True

# Global settings instance
_settings: Optional[Settings] = None

def get_settings() -> Settings:
    """Get or create the global settings instance."""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings

# Environment-specific settings
def get_development_settings() -> Settings:
    """Get development-specific settings."""
    return Settings(
        DEBUG=True,
        LOG_LEVEL="DEBUG",
        CORS_ORIGINS=["http://localhost:5173", "http://localhost:3000", "http://127.0.0.1:5173"]
    )

def get_production_settings() -> Settings:
    """Get production-specific settings."""
    return Settings(
        DEBUG=False,
        LOG_LEVEL="INFO",
        CORS_ORIGINS=os.getenv("CORS_ORIGINS", "").split(",")
    )

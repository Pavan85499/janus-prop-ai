"""
Configuration settings for Janus Prop AI Backend

This module provides centralized configuration management using Pydantic settings.
"""

import os
from typing import List, Optional, Dict, Any
from pathlib import Path
from pydantic_settings import BaseSettings
from pydantic import Field, field_validator

class Settings(BaseSettings):
    """Application settings with environment variable support."""
    
    # Application Configuration
    APP_NAME: str = "Janus Prop AI Backend"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = Field(default=False, env="DEBUG")
    ENVIRONMENT: str = Field(default="development", env="ENVIRONMENT")
    
    # Server Configuration
    HOST: str = Field(default="0.0.0.0", env="HOST")
    PORT: int = Field(default=8000, env="PORT")
    WORKERS: int = Field(default=1, env="WORKERS")
    
    # CORS Configuration
    CORS_ORIGINS: str = Field(
        default="http://localhost:5173,http://localhost:3000,http://localhost:8080,http://127.0.0.1:5173,http://127.0.0.1:3000,http://127.0.0.1:8080",
        env="CORS_ORIGINS"
    )
    CORS_ALLOW_CREDENTIALS: bool = Field(default=True, env="CORS_ALLOW_CREDENTIALS")
    CORS_ALLOW_METHODS: List[str] = Field(default=["GET", "POST", "PUT", "DELETE", "OPTIONS"], env="CORS_ALLOW_METHODS")
    CORS_ALLOW_HEADERS: List[str] = Field(default=["*"], env="CORS_ALLOW_HEADERS")
    
    # Database Configuration
    DATABASE_URL: str = Field(
        default="postgresql://user:password@localhost:5432/janus_prop_ai",
        env="DATABASE_URL"
    )
    DATABASE_POOL_SIZE: int = Field(default=10, env="DATABASE_POOL_SIZE")
    DATABASE_MAX_OVERFLOW: int = Field(default=20, env="DATABASE_MAX_OVERFLOW")
    DATABASE_POOL_TIMEOUT: int = Field(default=30, env="DATABASE_POOL_TIMEOUT")
    DATABASE_ECHO: bool = Field(default=False, env="DATABASE_ECHO")
    DATABASE_ECHO_POOL: bool = Field(default=False, env="DATABASE_ECHO_POOL")
    
    # Supabase Configuration
    SUPABASE_PROJECT_ID: Optional[str] = Field(default=None, env="SUPABASE_PROJECT_ID")
    SUPABASE_SERVICE_ROLE_KEY: Optional[str] = Field(default=None, env="SUPABASE_SERVICE_ROLE_KEY")
    SUPABASE_URL: Optional[str] = Field(default=None, env="SUPABASE_URL")
    SUPABASE_ANON_KEY: Optional[str] = Field(default=None, env="SUPABASE_ANON_KEY")
    
    # Frontend Configuration (VITE_ prefixed variables)
    VITE_SUPABASE_PROJECT_ID: Optional[str] = Field(default=None, env="VITE_SUPABASE_PROJECT_ID")
    VITE_SUPABASE_PUBLISHABLE_KEY: Optional[str] = Field(default=None, env="VITE_SUPABASE_PUBLISHABLE_KEY")
    VITE_SUPABASE_URL: Optional[str] = Field(default=None, env="VITE_SUPABASE_URL")
    VITE_API_BASE_URL: Optional[str] = Field(default=None, env="VITE_API_BASE_URL")
    VITE_ENABLE_REAL_TIME_UPDATES: Optional[str] = Field(default=None, env="VITE_ENABLE_REAL_TIME_UPDATES")
    VITE_ENABLE_AGENT_CONSOLE: Optional[str] = Field(default=None, env="VITE_ENABLE_AGENT_CONSOLE")
    VITE_DEBUG_MODE: Optional[str] = Field(default=None, env="VITE_DEBUG_MODE")
    VITE_LOG_LEVEL: Optional[str] = Field(default=None, env="VITE_LOG_LEVEL")
    
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
    REDIS_SOCKET_TIMEOUT: int = Field(default=5, env="REDIS_SOCKET_TIMEOUT")
    REDIS_SOCKET_CONNECT_TIMEOUT: int = Field(default=5, env="REDIS_SOCKET_CONNECT_TIMEOUT")
    
    # Email Configuration
    EMAIL_ENABLED: bool = Field(default=False, env="EMAIL_ENABLED")
    EMAIL_HOST: Optional[str] = Field(default=None, env="EMAIL_HOST")
    EMAIL_PORT: int = Field(default=587, env="EMAIL_PORT")
    EMAIL_USERNAME: Optional[str] = Field(default=None, env="EMAIL_USERNAME")
    EMAIL_PASSWORD: Optional[str] = Field(default=None, env="EMAIL_PASSWORD")
    EMAIL_USE_TLS: bool = Field(default=True, env="EMAIL_USE_TLS")
    EMAIL_USE_SSL: bool = Field(default=False, env="EMAIL_USE_SSL")
    EMAIL_FROM_ADDRESS: Optional[str] = Field(default=None, env="EMAIL_FROM_ADDRESS")
    EMAIL_FROM_NAME: str = Field(default="Janus Prop AI", env="EMAIL_FROM_NAME")
    
    # File Storage Configuration
    STORAGE_TYPE: str = Field(default="local", env="STORAGE_TYPE")  # local, s3, gcs, azure
    STORAGE_BUCKET: Optional[str] = Field(default=None, env="STORAGE_BUCKET")
    STORAGE_REGION: Optional[str] = Field(default=None, env="STORAGE_REGION")
    
    # AWS S3 Configuration
    AWS_ACCESS_KEY_ID: Optional[str] = Field(default=None, env="AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY: Optional[str] = Field(default=None, env="AWS_SECRET_ACCESS_KEY")
    AWS_S3_BUCKET: Optional[str] = Field(default=None, env="AWS_S3_BUCKET")
    AWS_S3_REGION: Optional[str] = Field(default=None, env="AWS_S3_REGION")
    AWS_S3_ENDPOINT_URL: Optional[str] = Field(default=None, env="AWS_S3_ENDPOINT_URL")
    
    # Google Cloud Storage Configuration
    GCS_PROJECT_ID: Optional[str] = Field(default=None, env="GCS_PROJECT_ID")
    GCS_BUCKET_NAME: Optional[str] = Field(default=None, env="GCS_BUCKET_NAME")
    GCS_CREDENTIALS_FILE: Optional[str] = Field(default=None, env="GCS_CREDENTIALS_FILE")
    
    # Azure Blob Storage Configuration
    AZURE_STORAGE_ACCOUNT: Optional[str] = Field(default=None, env="AZURE_STORAGE_ACCOUNT")
    AZURE_STORAGE_KEY: Optional[str] = Field(default=None, env="AZURE_STORAGE_KEY")
    AZURE_CONTAINER_NAME: Optional[str] = Field(default=None, env="AZURE_CONTAINER_NAME")
    
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
    
    # Additional Real Estate APIs
    MLS_API_KEY: Optional[str] = Field(default=None, env="MLS_API_KEY")
    PROPERTY_DATA_API_KEY: Optional[str] = Field(default=None, env="PROPERTY_DATA_API_KEY")
    REALTY_MOLE_API_KEY: Optional[str] = Field(default=None, env="REALTY_MOLE_API_KEY")
    RENT_SPREE_API_KEY: Optional[str] = Field(default=None, env="RENT_SPREE_API_KEY")
    
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
    RATE_LIMIT_ENABLED: bool = Field(default=True, env="RATE_LIMIT_ENABLED")
    
    # Logging Configuration
    LOG_LEVEL: str = Field(default="INFO", env="LOG_LEVEL")
    LOG_FILE: Optional[str] = Field(default=None, env="LOG_FILE")
    LOG_MAX_SIZE: int = Field(default=100, env="LOG_MAX_SIZE")  # MB
    LOG_BACKUP_COUNT: int = Field(default=5, env="LOG_BACKUP_COUNT")
    LOG_FORMAT: str = Field(default="%(asctime)s - %(name)s - %(levelname)s - %(message)s", env="LOG_FORMAT")
    
    # Agent Configuration
    MAX_CONCURRENT_AGENTS: int = Field(default=10, env="MAX_CONCURRENT_AGENTS")
    MAX_CONCURRENT_AGENT_TASKS: int = Field(default=5, env="MAX_CONCURRENT_AGENT_TASKS")
    AGENT_TIMEOUT: int = Field(default=300, env="AGENT_TIMEOUT")  # seconds
    AGENT_HEARTBEAT_TIMEOUT: int = Field(default=300, env="AGENT_HEARTBEAT_TIMEOUT")
    AGENT_HEALTH_CHECK_INTERVAL: int = Field(default=30, env="AGENT_HEALTH_CHECK_INTERVAL")
    AGENT_MEMORY_SIZE: int = Field(default=1000, env="AGENT_MEMORY_SIZE")
    
    # Real-time Configuration
    WEBSOCKET_HEARTBEAT_INTERVAL: int = Field(default=30, env="WEBSOCKET_HEARTBEAT_INTERVAL")
    REALTIME_UPDATE_INTERVAL: int = Field(default=5, env="REALTIME_UPDATE_INTERVAL")  # seconds
    WEBSOCKET_MAX_CONNECTIONS: int = Field(default=1000, env="WEBSOCKET_MAX_CONNECTIONS")
    
    # Data Processing
    MAX_PROPERTIES_PER_REQUEST: int = Field(default=1000, env="MAX_PROPERTIES_PER_REQUEST")
    DATA_SYNC_INTERVAL: int = Field(default=300, env="DATA_SYNC_INTERVAL")  # seconds
    CACHE_TTL_SECONDS: int = Field(default=1800, env="CACHE_TTL_SECONDS")
    MAX_PAGE_SIZE: int = Field(default=100, env="MAX_PAGE_SIZE")
    DEFAULT_PAGE_SIZE: int = Field(default=20, env="DEFAULT_PAGE_SIZE")
    DATA_BATCH_SIZE: int = Field(default=100, env="DATA_BATCH_SIZE")
    
    # File Upload Configuration
    MAX_FILE_SIZE: int = Field(default=50 * 1024 * 1024, env="MAX_FILE_SIZE")  # 50MB
    UPLOAD_DIR: str = Field(default="uploads", env="UPLOAD_DIR")
    ALLOWED_FILE_TYPES: List[str] = Field(default=["jpg", "jpeg", "png", "pdf", "doc", "docx", "xls", "xlsx"], env="ALLOWED_FILE_TYPES")
    MAX_FILES_PER_UPLOAD: int = Field(default=10, env="MAX_FILES_PER_UPLOAD")
    
    # Monitoring and Metrics
    ENABLE_METRICS: bool = Field(default=True, env="ENABLE_METRICS")
    METRICS_PORT: int = Field(default=9090, env="METRICS_PORT")
    METRICS_PATH: str = Field(default="/metrics", env="METRICS_PATH")
    HEALTH_CHECK_PATH: str = Field(default="/health", env="HEALTH_CHECK_PATH")
    
    # External Services
    SENTRY_DSN: Optional[str] = Field(default=None, env="SENTRY_DSN")
    SENTRY_ENVIRONMENT: str = Field(default="development", env="SENTRY_ENVIRONMENT")
    SENTRY_TRACES_SAMPLE_RATE: float = Field(default=1.0, env="SENTRY_TRACES_SAMPLE_RATE")
    
    # Background Tasks
    ENABLE_BACKGROUND_TASKS: bool = Field(default=True, env="ENABLE_BACKGROUND_TASKS")
    BACKGROUND_TASK_WORKERS: int = Field(default=4, env="BACKGROUND_TASK_WORKERS")
    BACKGROUND_TASK_MAX_RETRIES: int = Field(default=3, env="BACKGROUND_TASK_MAX_RETRIES")
    BACKGROUND_TASK_RETRY_DELAY: int = Field(default=60, env="BACKGROUND_TASK_RETRY_DELAY")
    
    # Search Configuration
    ELASTICSEARCH_URL: Optional[str] = Field(default=None, env="ELASTICSEARCH_URL")
    ELASTICSEARCH_USERNAME: Optional[str] = Field(default=None, env="ELASTICSEARCH_USERNAME")
    ELASTICSEARCH_PASSWORD: Optional[str] = Field(default=None, env="ELASTICSEARCH_PASSWORD")
    ELASTICSEARCH_INDEX_PREFIX: str = Field(default="janus_prop_ai", env="ELASTICSEARCH_INDEX_PREFIX")
    
    # Notification Configuration
    ENABLE_NOTIFICATIONS: bool = Field(default=True, env="ENABLE_NOTIFICATIONS")
    NOTIFICATION_CHANNELS: List[str] = Field(default=["email", "webhook"], env="NOTIFICATION_CHANNELS")
    WEBHOOK_URL: Optional[str] = Field(default=None, env="WEBHOOK_URL")
    WEBHOOK_SECRET: Optional[str] = Field(default=None, env="WEBHOOK_SECRET")
    
    # Feature Flags
    ENABLE_AI_FEATURES: bool = Field(default=True, env="ENABLE_AI_FEATURES")
    ENABLE_PROPERTY_ANALYSIS: bool = Field(default=True, env="ENABLE_PROPERTY_ANALYSIS")
    ENABLE_MARKET_INSIGHTS: bool = Field(default=True, env="ENABLE_MARKET_INSIGHTS")
    ENABLE_PREDICTIVE_MODELING: bool = Field(default=True, env="ENABLE_PREDICTIVE_MODELING")
    
    # API Versioning
    API_VERSION: str = Field(default="v1", env="API_VERSION")
    API_PREFIX: str = Field(default="/api", env="API_PREFIX")
    
    # Performance Configuration
    ENABLE_COMPRESSION: bool = Field(default=True, env="ENABLE_COMPRESSION")
    ENABLE_CACHING: bool = Field(default=True, env="ENABLE_CACHING")
    CACHE_TIMEOUT: int = Field(default=300, env="CACHE_TIMEOUT")
    REQUEST_TIMEOUT: int = Field(default=30, env="REQUEST_TIMEOUT")
    
    # Development Configuration
    ENABLE_SWAGGER: bool = Field(default=True, env="ENABLE_SWAGGER")
    ENABLE_RELOAD: bool = Field(default=False, env="ENABLE_RELOAD")
    ENABLE_DEBUG_TOOLBAR: bool = Field(default=False, env="ENABLE_DEBUG_TOOLBAR")
    
    @property
    def cors_origins_list(self) -> List[str]:
        """Get CORS origins as a list."""
        if isinstance(self.CORS_ORIGINS, str):
            if "," in self.CORS_ORIGINS:
                return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]
            elif self.CORS_ORIGINS.strip():
                return [self.CORS_ORIGINS.strip()]
        return [
            "http://localhost:5173",
            "http://localhost:3000", 
            "http://localhost:8080",
            "http://127.0.0.1:5173",
            "http://127.0.0.1:3000",
            "http://127.0.0.1:8080"
        ]
    
    @property
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.ENVIRONMENT.lower() in ["production", "prod"]
    
    @property
    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.ENVIRONMENT.lower() in ["development", "dev"]
    
    @property
    def is_testing(self) -> bool:
        """Check if running in testing environment."""
        return self.ENVIRONMENT.lower() in ["testing", "test"]
    
    @field_validator("SECRET_KEY", mode="before")
    @classmethod
    def validate_secret_key(cls, v):
        if v == "your-secret-key-here-change-in-production" or v == "your_secret_key_here":
            import secrets
            return secrets.token_urlsafe(32)
        return v
    
    @field_validator("CORS_ALLOW_METHODS", mode="before")
    @classmethod
    def validate_cors_methods(cls, v):
        if isinstance(v, str):
            return [method.strip() for method in v.split(",")]
        return v
    
    @field_validator("CORS_ALLOW_HEADERS", mode="before")
    @classmethod
    def validate_cors_headers(cls, v):
        if isinstance(v, str):
            return [header.strip() for header in v.split(",")]
        return v
    
    @field_validator("ALLOWED_FILE_TYPES", mode="before")
    @classmethod
    def validate_file_types(cls, v):
        if isinstance(v, str):
            return [ftype.strip() for ftype in v.split(",")]
        return v
    
    @field_validator("NOTIFICATION_CHANNELS", mode="before")
    @classmethod
    def validate_notification_channels(cls, v):
        if isinstance(v, str):
            return [channel.strip() for channel in v.split(",")]
        return v
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True
        extra = "ignore"  # Ignore extra environment variables that aren't defined in the model

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
        CORS_ORIGINS=["http://localhost:5173", "http://localhost:3000", "http://127.0.0.1:5173"],
        ENABLE_SWAGGER=True,
        ENABLE_RELOAD=True,
        DATABASE_ECHO=True
    )

def get_production_settings() -> Settings:
    """Get production-specific settings."""
    return Settings(
        DEBUG=False,
        LOG_LEVEL="INFO",
        CORS_ORIGINS=os.getenv("CORS_ORIGINS", "").split(","),
        ENABLE_SWAGGER=False,
        ENABLE_RELOAD=False,
        DATABASE_ECHO=False,
        ENABLE_COMPRESSION=True,
        ENABLE_CACHING=True
    )

def get_testing_settings() -> Settings:
    """Get testing-specific settings."""
    return Settings(
        DEBUG=True,
        LOG_LEVEL="DEBUG",
        DATABASE_URL="sqlite:///./test.db",
        REDIS_URL="redis://localhost:6379/1",
        ENABLE_METRICS=False,
        ENABLE_BACKGROUND_TASKS=False
    )

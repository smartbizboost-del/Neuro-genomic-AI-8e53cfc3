"""
Environment and configuration management for multi-deployment scenarios.
Supports: local development, docker-compose, Streamlit Cloud, Azure, ngrok tunneling.
"""

import os
from enum import Enum
from typing import Optional
from functools import lru_cache


class Environment(Enum):
    """Deployment environment types."""
    LOCAL = "local"                    # Local development (localhost)
    DOCKER_COMPOSE = "docker_compose" # Docker compose setup
    STREAMLIT_CLOUD = "streamlit_cloud"  # Streamlit Cloud deployment
    AZURE = "azure"                   # Azure VM deployment
    CLOUD_GENERIC = "cloud_generic"   # Generic cloud (ngrok, other)


class AppConfig:
    """Centralized configuration for all environments."""
    
    def __init__(self):
        self.environment = self._detect_environment()
        self.debug = os.getenv("DEBUG", "false").lower() == "true"
        
    @staticmethod
    def _detect_environment() -> Environment:
        """Auto-detect the current environment from system indicators."""
        
        # Streamlit Cloud detection
        if os.getenv("STREAMLIT_APP_ID") or os.getenv("STREAMLIT_CLOUD"):
            return Environment.STREAMLIT_CLOUD
        
        # Docker Compose detection
        if os.getenv("DOCKER_COMPOSE") == "true" or os.path.exists("/.dockerenv"):
            return Environment.DOCKER_COMPOSE
        
        # Azure detection (cloud-init sets this)
        if os.getenv("AZURE_DEPLOYMENT") == "true":
            return Environment.AZURE
        
        # ngrok or generic cloud (has public API_URL)
        api_url = os.getenv("API_URL", "").strip()
        if api_url and not api_url.startswith("http://127.0.0.1") and not api_url.startswith("http://localhost"):
            return Environment.CLOUD_GENERIC
        
        # Default to local
        return Environment.LOCAL
    
    @property
    def is_local(self) -> bool:
        return self.environment == Environment.LOCAL
    
    @property
    def is_cloud(self) -> bool:
        return self.environment in [Environment.STREAMLIT_CLOUD, Environment.AZURE, Environment.CLOUD_GENERIC]
    
    @property
    def is_docker(self) -> bool:
        return self.environment == Environment.DOCKER_COMPOSE
    
    @property
    def api_url(self) -> str:
        """Get the API URL for the current environment."""
        env_url = os.getenv("API_URL", "").strip()
        
        if env_url:
            return env_url
        
        match self.environment:
            case Environment.LOCAL:
                return "http://127.0.0.1:8000"
            case Environment.DOCKER_COMPOSE:
                return "http://api:8000"
            case Environment.STREAMLIT_CLOUD:
                # Cloud requires explicit API_URL - will be caught by startup validation
                return ""
            case Environment.AZURE:
                # Will be set via environment variable or cloud-init
                return os.getenv("AZURE_API_URL", "")
            case Environment.CLOUD_GENERIC:
                return env_url
            case _:
                return ""
    
    @property
    def database_url(self) -> str:
        """Get database URL appropriate for environment."""
        env_db = os.getenv("DATABASE_URL", "").strip()
        
        if env_db:
            return env_db
        
        match self.environment:
            case Environment.LOCAL:
                # Use SQLite locally
                return "sqlite:///./neuro_genomic.db"
            case Environment.DOCKER_COMPOSE:
                return "postgresql://neuro_user:neuro_pass@postgres:5432/neuro_genomic"
            case Environment.STREAMLIT_CLOUD:
                # Cloud should provide DATABASE_URL
                return os.getenv("DATABASE_URL", "")
            case Environment.AZURE:
                return "postgresql://neuro_user:neuro_pass@postgres:5432/neuro_genomic"
            case Environment.CLOUD_GENERIC:
                return os.getenv("DATABASE_URL", "")
            case _:
                return "sqlite:///./neuro_genomic.db"
    
    @property
    def redis_url(self) -> str:
        """Get Redis URL appropriate for environment."""
        env_redis = os.getenv("REDIS_URL", "").strip()
        
        if env_redis:
            return env_redis
        
        match self.environment:
            case Environment.LOCAL:
                return "redis://localhost:6379/0"
            case Environment.DOCKER_COMPOSE:
                return "redis://redis:6379/0"
            case Environment.AZURE:
                return "redis://redis:6379/0"
            case Environment.CLOUD_GENERIC:
                return os.getenv("REDIS_URL", "redis://localhost:6379/0")
            case _:
                return "redis://localhost:6379/0"
    
    @property
    def storage_backend(self) -> str:
        """Get storage backend for file uploads."""
        env_storage = os.getenv("STORAGE_BACKEND", "").strip().lower()
        
        if env_storage in ["s3", "minio", "local"]:
            return env_storage
        
        match self.environment:
            case Environment.LOCAL:
                return "local"
            case Environment.DOCKER_COMPOSE:
                return "minio"  # MinIO in docker-compose
            case Environment.AZURE:
                return "s3"  # Azure Blob Storage via S3 API
            case Environment.CLOUD_GENERIC:
                return "local"  # Fallback
            case _:
                return "local"
    
    @property
    def features(self) -> dict:
        """Get feature flags for current environment."""
        return {
            "auth_enabled": True,
            "file_upload": True,
            "ecg_analysis": True,
            "export_results": self.environment != Environment.LOCAL,  # Export only in cloud
            "admin_dashboard": self.is_local or self.is_docker,  # Admin only local/docker
            "monitoring": self.is_cloud,  # Monitoring in cloud
            "caching": self.environment != Environment.LOCAL,  # Cache in production
            "background_tasks": self.environment != Environment.STREAMLIT_CLOUD,  # Streamlit Cloud doesn't support long-running tasks
        }
    
    @property
    def log_level(self) -> str:
        """Get log level for environment."""
        return "DEBUG" if self.debug or self.is_local else "INFO"
    
    @property
    def cors_origins(self) -> list[str]:
        """Get allowed CORS origins."""
        if self.is_local:
            return ["*"]  # Allow all in local dev
        
        # Cloud: be restrictive
        origins = [
            "https://neurogenomic2.streamlit.app",
        ]
        
        # Add ngrok domain if detected
        api_url = self.api_url
        if "ngrok" in api_url:
            origins.append("https://neurogenomic2.streamlit.app")
        
        return origins
    
    def __repr__(self) -> str:
        return (
            f"AppConfig(\n"
            f"  environment={self.environment.value}\n"
            f"  api_url={self.api_url}\n"
            f"  database={self.database_url}\n"
            f"  storage={self.storage_backend}\n"
            f"  debug={self.debug}\n"
            f")"
        )


@lru_cache(maxsize=1)
def get_config() -> AppConfig:
    """Get singleton config instance."""
    return AppConfig()

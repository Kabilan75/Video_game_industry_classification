"""
Configuration settings for the application.
Loads environment variables and provides configuration objects.
"""

from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Application
    app_name: str = "Games Industry Jobs Dashboard"
    debug: bool = False
    log_level: str = "INFO"
    
    # Database
    database_url: str = "sqlite:///./games_industry_jobs.db"
    db_pool_size: int = 20
    db_max_overflow: int = 10
    
    # Redis
    redis_url: str = "redis://localhost:6379/0"
    redis_cache_ttl: int = 3600  # 1 hour in seconds
    
    # Security
    secret_key: str = "dev-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # Email (for alerts)
    smtp_host: str = ""
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""
    alert_email: str = ""
    
    # Pagination
    default_page_size: int = 50
    max_page_size: int = 100
    
    # Rate limiting
    rate_limit_per_minute: int = 100
    
    # Scraper
    scraper_user_agent: str = "Mozilla/5.0"
    scraper_delay: int = 2
    scraper_concurrent_requests: int = 16
    
    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()

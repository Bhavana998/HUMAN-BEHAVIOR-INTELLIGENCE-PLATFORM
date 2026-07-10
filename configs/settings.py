"""Application settings loaded from environment variables."""

from typing import List
from pydantic import AnyUrl, validator  # <-- import AnyUrl instead of PostgresDsn
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Main settings class."""

    # Application
    APP_NAME: str = "Human Behavior Intelligence Platform"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Database – now accepts SQLite, PostgreSQL, etc.
    DATABASE_URL: AnyUrl  # <-- changed from PostgresDsn

    # Redis (for Celery)
    REDIS_URL: AnyUrl  # <-- also AnyUrl for flexibility

    # Celery
    CELERY_BROKER_URL: str
    CELERY_RESULT_BACKEND: str

    # MLflow
    MLFLOW_TRACKING_URI: str = "http://localhost:5000"
    MLFLOW_EXPERIMENT_NAME: str = "behavior_intelligence"

    # Model storage
    MODEL_STORAGE_PATH: str = "/models"

    # File upload
    UPLOAD_DIR: str = "/uploads"
    MAX_UPLOAD_SIZE_MB: int = 100

    # Security
    ALLOWED_ORIGINS: List[str] = ["*"]
    RATE_LIMIT_PER_MINUTE: int = 60

    # Logging
    LOG_LEVEL: str = "INFO"

    @validator("CELERY_BROKER_URL", pre=True)
    def default_broker(cls, v, values):
        return v or values.get("REDIS_URL", "").replace("redis://", "redis://").replace("?ssl=true", "")

    @validator("CELERY_RESULT_BACKEND", pre=True)
    def default_backend(cls, v, values):
        return v or values.get("REDIS_URL", "").replace("redis://", "redis://").replace("?ssl=true", "")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


settings = Settings()
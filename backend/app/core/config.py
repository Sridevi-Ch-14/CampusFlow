import os
from typing import List, Union
from pydantic import Field, AnyHttpUrl, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=True
    )

    PROJECT_NAME: str = "CampusFlow"
    API_V1_STR: str = "/api/v1"
    
    # Environment
    ENVIRONMENT: str = Field(default="development")
    DEBUG: bool = Field(default=True)
    
    # Security / Auth
    SECRET_KEY: str = Field(default="campusflow-super-secret-jwt-key-change-in-production-2026")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 1 day
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # Database (MySQL)
    MYSQL_HOST: str = Field(default="localhost")
    MYSQL_PORT: int = Field(default=3306)
    MYSQL_USER: str = Field(default="root")
    MYSQL_PASSWORD: str = Field(default="password")
    MYSQL_DATABASE: str = Field(default="campusflow_db")
    DATABASE_URL: Union[str, None] = None

    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def assemble_db_connection(cls, v: Union[str, None], info) -> str:
        if isinstance(v, str) and v.strip():
            return v
        values = info.data
        host = values.get("MYSQL_HOST", "localhost")
        port = values.get("MYSQL_PORT", 3306)
        user = values.get("MYSQL_USER", "root")
        password = values.get("MYSQL_PASSWORD", "password")
        db = values.get("MYSQL_DATABASE", "campusflow_db")
        return f"mysql+pymysql://{user}:{password}@{host}:{port}/{db}"

    # Async Database URL
    @property
    def ASYNC_DATABASE_URL(self) -> str:
        url = self.DATABASE_URL or ""
        if url.startswith("mysql+pymysql://"):
            return url.replace("mysql+pymysql://", "mysql+aiomysql://")
        return url

    # Storage (local or s3)
    STORAGE_TYPE: str = Field(default="local")  # 'local' or 's3'
    LOCAL_STORAGE_DIR: str = Field(default="uploads")
    
    S3_ENDPOINT_URL: Union[str, None] = None
    S3_ACCESS_KEY: Union[str, None] = None
    S3_SECRET_KEY: Union[str, None] = None
    S3_BUCKET_NAME: str = Field(default="campusflow-attachments")
    S3_REGION: str = Field(default="us-east-1")

    # Redis & Celery
    REDIS_HOST: str = Field(default="localhost")
    REDIS_PORT: int = Field(default=6379)
    REDIS_URL: Union[str, None] = None

    @field_validator("REDIS_URL", mode="before")
    @classmethod
    def assemble_redis_connection(cls, v: Union[str, None], info) -> str:
        if isinstance(v, str) and v.strip():
            return v
        values = info.data
        host = values.get("REDIS_HOST", "localhost")
        port = values.get("REDIS_PORT", 6379)
        return f"redis://{host}:{port}/0"

    # CORS
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]

settings = Settings()

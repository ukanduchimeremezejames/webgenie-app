"""
Core configuration using Pydantic BaseSettings.
Supports environment variables and .env files.
"""

import os
from pathlib import Path
from typing import Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables and .env files."""

    # App metadata
    app_name: str = "WebGenie Backend"
    app_version: str = "1.0.0"
    environment: str = "development"

    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    reload: bool = True
    debug: bool = True

    # Database
    database_url: str = "sqlite:///./webgenie.db"

    # Celery/Redis
    redis_url: str = "redis://localhost:6379"
    celery_broker_url: str = "redis://localhost:6379/0"
    celery_result_backend: str = "redis://localhost:6379/1"

    # CORS
    cors_origins: list[str] = [
        "http://localhost:3000",
        "http://localhost:8000",
        "http://localhost:5173",
    ]
    cors_allow_credentials: bool = True
    cors_allow_methods: list[str] = ["*"]
    cors_allow_headers: list[str] = ["*"]

    # Paths
    base_dir: Path = Path(__file__).resolve().parent.parent.parent
    data_dir: Path = base_dir / "data"
    results_dir: Path = data_dir / "results"
    datasets_dir: Path = data_dir / "datasets"

    # Logging
    log_level: str = "INFO"
    log_format: str = "json"

    # Job configuration
    job_timeout: int = 3600  # 1 hour in seconds
    max_concurrent_jobs: int = 4

    # Beeline/Algorithm configuration
    beeline_timeout: int = 1800  # 30 minutes
    supported_algorithms: list[str] = [
        "GRNBoost2",
        "SCENIC",
        "PIDC",
        "CLR",
        "ARACNE",
        "NES",
        "Inferelator",
        "pySCENIC",
    ]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False

    def __init__(self, **data):
        super().__init__(**data)
        # Ensure directories exist
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.results_dir.mkdir(parents=True, exist_ok=True)
        self.datasets_dir.mkdir(parents=True, exist_ok=True)


# Global settings instance
settings = Settings()

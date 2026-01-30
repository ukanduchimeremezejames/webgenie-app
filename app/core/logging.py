"""
Structured JSON logging configuration.
Supports contextual logging with job IDs and request tracking.
"""

import json
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

from app.core.config import settings


class JSONFormatter(logging.Formatter):
    """Custom JSON formatter for structured logging."""

    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON."""
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        # Add optional fields if present
        if hasattr(record, "job_id"):
            log_data["job_id"] = record.job_id
        if hasattr(record, "dataset_id"):
            log_data["dataset_id"] = record.dataset_id
        if hasattr(record, "request_id"):
            log_data["request_id"] = record.request_id

        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_data)


class PlainFormatter(logging.Formatter):
    """Plain text formatter for human-readable logs."""

    def format(self, record: logging.LogRecord) -> str:
        """Format log record as plain text."""
        base_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        formatter = logging.Formatter(base_format)
        return formatter.format(record)


def setup_logging() -> logging.Logger:
    """Configure root logger with appropriate handlers."""
    root_logger = logging.getLogger()
    root_logger.setLevel(settings.log_level)

    # Remove existing handlers to avoid duplicates
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(settings.log_level)

    if settings.log_format == "json":
        console_handler.setFormatter(JSONFormatter())
    else:
        console_handler.setFormatter(PlainFormatter())

    root_logger.addHandler(console_handler)

    # File handler (optional)
    if settings.environment == "production":
        log_file = settings.base_dir / "logs" / "app.log"
        log_file.parent.mkdir(parents=True, exist_ok=True)

        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(JSONFormatter())
        root_logger.addHandler(file_handler)

    return root_logger


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance with the specified name."""
    return logging.getLogger(name)


class JobContextFilter(logging.Filter):
    """Filter to inject job context into log records."""

    def __init__(self, job_id: Optional[str] = None):
        super().__init__()
        self.job_id = job_id

    def filter(self, record: logging.LogRecord) -> bool:
        """Add job_id to log record."""
        if self.job_id:
            record.job_id = self.job_id
        return True


# Initialize logging on module import
logger = setup_logging()

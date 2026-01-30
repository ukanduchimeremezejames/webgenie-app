"""Pydantic models for Job management."""

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class JobStatus(str, Enum):
    """Job execution status."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class JobCreate(BaseModel):
    """Request model for creating a new job."""

    dataset_id: str = Field(..., description="ID of the dataset to run inference on")
    algorithm: str = Field(..., description="Algorithm to use for GRN inference")
    params: Optional[dict] = Field(
        default_factory=dict,
        description="Algorithm-specific parameters",
    )

    class Config:
        json_schema_extra = {
            "example": {
                "dataset_id": "dataset_123",
                "algorithm": "GRNBoost2",
                "params": {
                    "treeMethod": "hist",
                    "dropin": 0.2,
                },
            }
        }


class JobResponse(BaseModel):
    """Response model for job details."""

    id: str
    dataset_id: str
    algorithm: str
    status: JobStatus
    params: dict
    started_at: Optional[datetime] = None
    ended_at: Optional[datetime] = None
    progress_percent: int = 0
    error_message: Optional[str] = None

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "job_abc123",
                "dataset_id": "dataset_123",
                "algorithm": "GRNBoost2",
                "status": "running",
                "params": {"treeMethod": "hist"},
                "started_at": "2024-01-27T10:30:00",
                "ended_at": None,
                "progress_percent": 45,
                "error_message": None,
            }
        }


class JobListResponse(BaseModel):
    """Response model for listing jobs."""

    total: int
    jobs: list[JobResponse]


class JobLogResponse(BaseModel):
    """Response model for job logs."""

    job_id: str
    logs: list[str] = Field(default_factory=list)
    timestamp: datetime = Field(default_factory=datetime.utcnow)

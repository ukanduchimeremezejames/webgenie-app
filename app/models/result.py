"""Pydantic models for Result management."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class ResultCreate(BaseModel):
    """Request model for creating a result record."""

    job_id: str = Field(..., description="Associated job ID")
    dataset_id: str = Field(..., description="Associated dataset ID")
    algorithm: str = Field(..., description="Algorithm used")
    summary: dict = Field(default_factory=dict, description="Result summary statistics")


class ResultResponse(BaseModel):
    """Response model for result details."""

    id: str
    job_id: str
    dataset_id: str
    algorithm: str
    summary: dict = Field(default_factory=dict)
    created_at: datetime
    updated_at: datetime
    output_files: list[str] = Field(default_factory=list)
    size_bytes: Optional[int] = None

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "result_123",
                "job_id": "job_abc123",
                "dataset_id": "dataset_123",
                "algorithm": "GRNBoost2",
                "summary": {
                    "edges_predicted": 5000,
                    "mean_weight": 0.45,
                    "max_weight": 0.99,
                },
                "created_at": "2024-01-27T11:30:00",
                "updated_at": "2024-01-27T11:30:00",
                "output_files": ["adjacency_matrix.csv", "metadata.json"],
                "size_bytes": 10000000,
            }
        }


class ResultListResponse(BaseModel):
    """Response model for listing results."""

    total: int
    results: list[ResultResponse]


class ResultSummary(BaseModel):
    """Summary statistics for a result."""

    job_id: str
    algorithm: str
    edges_predicted: int = 0
    mean_weight: float = 0.0
    max_weight: float = 0.0
    min_weight: float = 0.0
    execution_time_seconds: float = 0.0

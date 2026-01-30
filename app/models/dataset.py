"""Pydantic models for Dataset management."""

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class DatasetType(str, Enum):
    """Type of dataset."""

    EXPRESSION = "expression"
    PERTURBATION = "perturbation"
    SYNTHETIC = "synthetic"
    BENCHMARK = "benchmark"


class DatasetCreate(BaseModel):
    """Request model for registering a new dataset."""

    name: str = Field(..., description="Unique dataset name")
    description: Optional[str] = Field(None, description="Dataset description")
    dataset_type: DatasetType = Field(..., description="Type of dataset")
    file_path: str = Field(..., description="Path to dataset file")
    genes: Optional[int] = Field(None, description="Number of genes")
    samples: Optional[int] = Field(None, description="Number of samples")
    metadata: Optional[dict] = Field(default_factory=dict, description="Additional metadata")

    class Config:
        json_schema_extra = {
            "example": {
                "name": "hESC_dataset",
                "description": "Human embryonic stem cells",
                "dataset_type": "expression",
                "file_path": "/data/datasets/hESC.csv",
                "genes": 1000,
                "samples": 500,
                "metadata": {"source": "GEO", "species": "human"},
            }
        }


class DatasetResponse(BaseModel):
    """Response model for dataset details."""

    id: str
    name: str
    description: Optional[str] = None
    dataset_type: DatasetType
    file_path: str
    genes: Optional[int] = None
    samples: Optional[int] = None
    metadata: dict = Field(default_factory=dict)
    created_at: datetime
    updated_at: datetime
    size_bytes: Optional[int] = None
    is_hf_dataset: bool = Field(default=False, description="Whether this is a Hugging Face dataset")

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "dataset_123",
                "name": "hESC_dataset",
                "description": "Human embryonic stem cells",
                "dataset_type": "expression",
                "file_path": "/data/datasets/hESC.csv",
                "genes": 1000,
                "samples": 500,
                "metadata": {"source": "GEO"},
                "created_at": "2024-01-27T10:00:00",
                "updated_at": "2024-01-27T10:00:00",
                "size_bytes": 5000000,
            }
        }


class DatasetListResponse(BaseModel):
    """Response model for listing datasets."""

    total: int
    datasets: list[DatasetResponse]


class DatasetSchema(BaseModel):
    """Schema information for a dataset."""

    dataset_id: str
    columns: list[str]
    row_count: int
    column_count: int
    dtypes: dict[str, str]

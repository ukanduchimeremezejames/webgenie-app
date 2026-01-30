"""API endpoints for dataset management."""

from typing import Optional

from fastapi import APIRouter, HTTPException, Query

from app.models import DatasetCreate, DatasetListResponse, DatasetResponse, DatasetSchema
from app.services.datasets_service import DatasetsService

router = APIRouter(prefix="/datasets", tags=["datasets"])
datasets_service = DatasetsService()


@router.post("/", response_model=DatasetResponse, status_code=201)
async def register_dataset(dataset_create: DatasetCreate) -> DatasetResponse:
    """
    Register a new dataset.

    Request body should contain:
    - name: Unique dataset name
    - dataset_type: Type of dataset (expression, perturbation, synthetic, benchmark)
    - file_path: Path to dataset file
    - description: Optional description
    - genes: Optional number of genes
    - samples: Optional number of samples
    - metadata: Optional additional metadata
    """
    try:
        return datasets_service.register_dataset(dataset_create)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to register dataset: {str(e)}")


@router.get("/", response_model=DatasetListResponse)
async def list_datasets(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
) -> DatasetListResponse:
    """
    List all registered datasets with pagination.

    Query parameters:
    - skip: Number of records to skip (default: 0)
    - limit: Maximum records to return (default: 100, max: 1000)
    """
    datasets = datasets_service.list_datasets(skip=skip, limit=limit)
    total = datasets_service.count_datasets()
    return DatasetListResponse(total=total, datasets=datasets)


@router.get("/{dataset_id}", response_model=DatasetResponse)
async def get_dataset(dataset_id: str) -> DatasetResponse:
    """Get dataset details by ID."""
    dataset = datasets_service.get_dataset(dataset_id)
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    return dataset


@router.get("/{dataset_id}/schema", response_model=Optional[DatasetSchema])
async def get_dataset_schema(dataset_id: str) -> Optional[DatasetSchema]:
    """Get schema information for a dataset (columns, dtypes, row/column count)."""
    schema = datasets_service.get_dataset_schema(dataset_id)
    if not schema:
        raise HTTPException(status_code=404, detail="Dataset not found or schema unavailable")
    return schema


@router.delete("/{dataset_id}", status_code=204)
async def delete_dataset(dataset_id: str) -> None:
    """Delete a dataset by ID."""
    success = datasets_service.delete_dataset(dataset_id)
    if not success:
        raise HTTPException(status_code=404, detail="Dataset not found")

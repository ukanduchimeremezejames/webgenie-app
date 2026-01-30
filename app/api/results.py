"""API endpoints for results retrieval."""

from typing import Optional

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import FileResponse

from app.models import ResultListResponse, ResultResponse
from app.services.inference_service import ResultsService

router = APIRouter(prefix="/results", tags=["results"])
results_service = ResultsService()


@router.get("/", response_model=ResultListResponse)
async def list_results(
    dataset_id: Optional[str] = Query(None, description="Filter by dataset ID"),
    algorithm: Optional[str] = Query(None, description="Filter by algorithm"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
) -> ResultListResponse:
    """
    List results with optional filtering.

    Query parameters:
    - dataset_id: Optional dataset ID filter
    - algorithm: Optional algorithm filter
    - skip: Number of records to skip (default: 0)
    - limit: Maximum records to return (default: 100, max: 1000)
    """
    results = results_service.list_results(
        dataset_id=dataset_id,
        algorithm=algorithm,
        skip=skip,
        limit=limit,
    )
    total = results_service.count_results(dataset_id=dataset_id, algorithm=algorithm)
    return ResultListResponse(total=total, results=results)


@router.get("/{result_id}", response_model=ResultResponse)
async def get_result(result_id: str) -> ResultResponse:
    """Get result details by ID."""
    result = results_service.get_result(result_id)
    if not result:
        raise HTTPException(status_code=404, detail="Result not found")
    return result


@router.get("/{result_id}/files")
async def list_result_files(result_id: str) -> dict:
    """
    List output files for a result.

    Returns a list of filenames available for download.
    """
    result = results_service.get_result(result_id)
    if not result:
        raise HTTPException(status_code=404, detail="Result not found")

    files = results_service.get_result_files(result_id)
    return {
        "result_id": result_id,
        "files": [f.name for f in files],
    }


@router.get("/{result_id}/download/{filename}")
async def download_result_file(
    result_id: str,
    filename: str,
) -> FileResponse:
    """
    Download a specific output file from a result.

    Path parameters:
    - result_id: Result identifier
    - filename: Name of file to download
    """
    file_path = results_service.get_result_file(result_id, filename)
    if not file_path:
        raise HTTPException(status_code=404, detail="File not found")

    return FileResponse(
        path=file_path,
        filename=filename,
        media_type="application/octet-stream",
    )


@router.delete("/{result_id}", status_code=204)
async def delete_result(result_id: str) -> None:
    """Delete a result and associated files."""
    success = results_service.delete_result(result_id)
    if not success:
        raise HTTPException(status_code=404, detail="Result not found")

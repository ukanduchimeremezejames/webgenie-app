"""API endpoints for job management."""

from typing import Optional

from fastapi import APIRouter, HTTPException, Query

from app.models import JobCreate, JobListResponse, JobLogResponse, JobResponse
from app.services.datasets_service import DatasetsService
from app.services.jobs_service import JobsService

router = APIRouter(prefix="/jobs", tags=["jobs"])
jobs_service = JobsService()
datasets_service = DatasetsService()


@router.post("/", response_model=JobResponse, status_code=201)
async def submit_job(job_create: JobCreate) -> JobResponse:
    """
    Submit a new GRN inference job.

    Request body should contain:
    - dataset_id: ID of the dataset
    - algorithm: Algorithm to use (GRNBoost2, SCENIC, PIDC, etc.)
    - params: Optional algorithm-specific parameters
    """
    try:
        # Validate dataset exists
        dataset = datasets_service.get_dataset(job_create.dataset_id)
        if not dataset:
            raise HTTPException(status_code=404, detail="Dataset not found")

        # Create and submit job
        return jobs_service.create_job(job_create, dataset.file_path)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to submit job: {str(e)}")


@router.get("/", response_model=JobListResponse)
async def list_jobs(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
) -> JobListResponse:
    """
    List all jobs with pagination.

    Query parameters:
    - skip: Number of records to skip (default: 0)
    - limit: Maximum records to return (default: 100, max: 1000)
    """
    jobs = jobs_service.list_jobs(skip=skip, limit=limit)
    total = jobs_service.count_jobs()
    return JobListResponse(total=total, jobs=jobs)


@router.get("/{job_id}", response_model=JobResponse)
async def get_job(job_id: str) -> JobResponse:
    """Get job details by ID."""
    job = jobs_service.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job


@router.get("/{job_id}/logs", response_model=JobLogResponse)
async def get_job_logs(job_id: str) -> JobLogResponse:
    """
    Get execution logs for a job.

    Returns the log lines as a list of strings.
    """
    job = jobs_service.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    logs = jobs_service.get_job_logs(job_id)
    return JobLogResponse(job_id=job_id, logs=logs)


@router.delete("/{job_id}", status_code=204)
async def cancel_job(job_id: str) -> None:
    """
    Cancel a job.

    Only pending or running jobs can be cancelled.
    """
    success = jobs_service.cancel_job(job_id)
    if not success:
        raise HTTPException(
            status_code=400, detail="Job not found or cannot be cancelled"
        )

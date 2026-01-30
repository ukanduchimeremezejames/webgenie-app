"""Unit tests for jobs service."""

import pytest
from app.models import JobCreate, JobStatus


@pytest.mark.asyncio
async def test_create_job(jobs_service, sample_dataset_file):
    """Test creating a job."""
    job_create = JobCreate(
        dataset_id="dataset_123",
        algorithm="GRNBoost2",
        params={"n_jobs": 4},
    )

    result = jobs_service.create_job(job_create, sample_dataset_file)

    assert result.status == JobStatus.PENDING
    assert result.algorithm == "GRNBoost2"
    assert result.dataset_id == "dataset_123"


@pytest.mark.asyncio
async def test_get_job(jobs_service, sample_dataset_file):
    """Test retrieving a job."""
    job_create = JobCreate(
        dataset_id="dataset_123",
        algorithm="GRNBoost2",
    )

    created = jobs_service.create_job(job_create, sample_dataset_file)
    retrieved = jobs_service.get_job(created.id)

    assert retrieved is not None
    assert retrieved.id == created.id
    assert retrieved.algorithm == "GRNBoost2"


@pytest.mark.asyncio
async def test_list_jobs(jobs_service, sample_dataset_file):
    """Test listing jobs."""
    for i in range(3):
        job_create = JobCreate(
            dataset_id=f"dataset_{i}",
            algorithm="GRNBoost2",
        )
        jobs_service.create_job(job_create, sample_dataset_file)

    jobs = jobs_service.list_jobs()

    assert len(jobs) == 3
    assert jobs_service.count_jobs() == 3


@pytest.mark.asyncio
async def test_update_job_status(jobs_service, sample_dataset_file):
    """Test updating job status."""
    job_create = JobCreate(
        dataset_id="dataset_123",
        algorithm="GRNBoost2",
    )

    created = jobs_service.create_job(job_create, sample_dataset_file)
    updated = jobs_service.update_job_status(
        created.id,
        JobStatus.RUNNING,
        progress_percent=50,
    )

    assert updated.status == JobStatus.RUNNING
    assert updated.progress_percent == 50


@pytest.mark.asyncio
async def test_cancel_job(jobs_service, sample_dataset_file):
    """Test cancelling a job."""
    job_create = JobCreate(
        dataset_id="dataset_123",
        algorithm="GRNBoost2",
    )

    created = jobs_service.create_job(job_create, sample_dataset_file)
    success = jobs_service.cancel_job(created.id)

    assert success is True

    cancelled = jobs_service.get_job(created.id)
    assert cancelled.status == JobStatus.CANCELLED


@pytest.mark.asyncio
async def test_delete_job(jobs_service, sample_dataset_file):
    """Test deleting a job."""
    job_create = JobCreate(
        dataset_id="dataset_123",
        algorithm="GRNBoost2",
    )

    created = jobs_service.create_job(job_create, sample_dataset_file)
    success = jobs_service.delete_job(created.id)

    assert success is True
    assert jobs_service.get_job(created.id) is None

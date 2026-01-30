"""Asynchronous task registration and management."""

import json
import logging
import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional

from app.core import settings
from app.models import JobStatus
from app.workers.celery_app import celery_app

logger = logging.getLogger(__name__)


class JobDatabase:
    """Simple file-based job database."""

    def __init__(self):
        self.jobs_dir = settings.data_dir / "jobs"
        self.jobs_dir.mkdir(parents=True, exist_ok=True)

    def save_job(self, job_id: str, job_data: dict) -> None:
        """Save job metadata to file."""
        job_file = self.jobs_dir / f"{job_id}.json"
        with open(job_file, "w") as f:
            json.dump(job_data, f, indent=2, default=str)

    def get_job(self, job_id: str) -> Optional[dict]:
        """Retrieve job metadata."""
        job_file = self.jobs_dir / f"{job_id}.json"
        if not job_file.exists():
            return None
        with open(job_file) as f:
            return json.load(f)

    def list_jobs(self, skip: int = 0, limit: int = 100) -> tuple[list[dict], int]:
        """List all jobs with pagination."""
        job_files = sorted(self.jobs_dir.glob("*.json"), reverse=True)
        total = len(job_files)
        jobs = []
        for job_file in job_files[skip : skip + limit]:
            with open(job_file) as f:
                jobs.append(json.load(f))
        return jobs, total

    def delete_job(self, job_id: str) -> bool:
        """Delete job metadata."""
        job_file = self.jobs_dir / f"{job_id}.json"
        if not job_file.exists():
            return False
        job_file.unlink()
        return True

    def update_job_status(self, job_id: str, status: JobStatus, **updates) -> None:
        """Update job status and additional fields."""
        job_data = self.get_job(job_id)
        if job_data:
            job_data["status"] = status.value
            job_data.update(updates)
            job_data["updated_at"] = datetime.utcnow().isoformat()
            self.save_job(job_id, job_data)


# Global job database instance
job_db = JobDatabase()


@celery_app.task(bind=True, name="tasks.run_inference_job")
def run_inference_job(
    self,
    job_id: str,
    dataset_id: str,
    dataset_path: str,
    algorithm: str,
    params: Optional[dict] = None,
) -> dict:
    """
    Execute GRN inference job asynchronously.

    Args:
        job_id: Unique job identifier
        dataset_id: ID of the dataset
        dataset_path: Path to dataset file
        algorithm: Algorithm to use
        params: Algorithm parameters

    Returns:
        Job execution result
    """
    params = params or {}

    # Setup logging for this job
    task_logger = logging.getLogger(f"task.{job_id}")

    try:
        # Update job status to running
        output_dir = settings.results_dir / job_id
        output_dir.mkdir(parents=True, exist_ok=True)

        job_db.update_job_status(
            job_id,
            JobStatus.RUNNING,
            celery_task_id=self.request.id,
            started_at=datetime.utcnow().isoformat(),
        )

        task_logger.info(f"Job {job_id} started - Algorithm: {algorithm}")

        # Import runner here to avoid circular imports
        from app.services.runners.beeline_runner import run_beeline_pipeline

        # Execute pipeline
        result = run_beeline_pipeline(
            dataset_path=dataset_path,
            algorithm=algorithm,
            params=params,
            output_dir=output_dir,
            job_id=job_id,
        )

        # Update job status to completed
        job_db.update_job_status(
            job_id,
            JobStatus.COMPLETED,
            ended_at=datetime.utcnow().isoformat(),
            result=result,
            progress_percent=100,
        )

        task_logger.info(f"Job {job_id} completed successfully")

        return {
            "job_id": job_id,
            "status": "completed",
            "result": result,
        }

    except Exception as e:
        error_message = str(e)
        task_logger.error(f"Job {job_id} failed: {error_message}")

        # Update job status to failed
        job_db.update_job_status(
            job_id,
            JobStatus.FAILED,
            ended_at=datetime.utcnow().isoformat(),
            error_message=error_message,
        )

        return {
            "job_id": job_id,
            "status": "failed",
            "error": error_message,
        }


@celery_app.task(bind=True, name="tasks.cancel_job")
def cancel_job(self, job_id: str) -> dict:
    """
    Cancel a running job.

    Args:
        job_id: Job identifier

    Returns:
        Cancellation result
    """
    job_data = job_db.get_job(job_id)
    if not job_data:
        return {"status": "failed", "error": "Job not found"}

    # Revoke the task if it exists
    if "celery_task_id" in job_data:
        celery_app.control.revoke(job_data["celery_task_id"], terminate=True)

    # Update status
    job_db.update_job_status(job_id, JobStatus.CANCELLED)

    logger.info(f"Job {job_id} cancelled")

    return {"status": "cancelled", "job_id": job_id}

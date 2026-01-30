"""Service layer for job management."""

import json
import logging
import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional

from app.core import settings
from app.models import JobCreate, JobResponse, JobStatus
from app.workers.celery_app import celery_app

logger = logging.getLogger(__name__)


class JobsService:
    """Service for managing inference jobs."""

    def __init__(self):
        self.jobs_dir = settings.data_dir / "jobs"
        self.jobs_dir.mkdir(parents=True, exist_ok=True)

    def create_job(
        self,
        job_create: JobCreate,
        dataset_path: str,
    ) -> JobResponse:
        """
        Create and submit a new job.

        Args:
            job_create: Job creation request
            dataset_path: Path to dataset file

        Returns:
            JobResponse with job details
        """
        job_id = f"job_{uuid.uuid4().hex[:12]}"
        now = datetime.utcnow()

        job_data = {
            "id": job_id,
            "dataset_id": job_create.dataset_id,
            "algorithm": job_create.algorithm,
            "status": JobStatus.PENDING.value,
            "params": job_create.params or {},
            "started_at": None,
            "ended_at": None,
            "progress_percent": 0,
            "error_message": None,
            "created_at": now.isoformat(),
            "updated_at": now.isoformat(),
            "celery_task_id": None,
        }

        self._save_job(job_id, job_data)

        # Submit to Celery worker
        task = celery_app.send_task(
            "tasks.run_inference_job",
            args=[
                job_id,
                job_create.dataset_id,
                dataset_path,
                job_create.algorithm,
                job_create.params or {},
            ],
        )

        # Update job with task ID
        job_data["celery_task_id"] = task.id
        self._save_job(job_id, job_data)

        logger.info(f"Job created: {job_id} - Algorithm: {job_create.algorithm}")

        return JobResponse(**job_data)

    def get_job(self, job_id: str) -> Optional[JobResponse]:
        """
        Get job by ID.

        Args:
            job_id: Job identifier

        Returns:
            JobResponse or None if not found
        """
        job_data = self._load_job(job_id)
        if not job_data:
            return None

        # Convert datetime strings
        if job_data.get("started_at"):
            job_data["started_at"] = datetime.fromisoformat(job_data["started_at"])
        if job_data.get("ended_at"):
            job_data["ended_at"] = datetime.fromisoformat(job_data["ended_at"])

        return JobResponse(**job_data)

    def list_jobs(self, skip: int = 0, limit: int = 100) -> list[JobResponse]:
        """
        List all jobs with pagination.

        Args:
            skip: Number of records to skip
            limit: Maximum records to return

        Returns:
            List of JobResponse objects
        """
        job_files = sorted(self.jobs_dir.glob("*.json"), reverse=True)
        jobs = []

        for job_file in job_files[skip : skip + limit]:
            job_id = job_file.stem
            job_data = self._load_job(job_id)
            if job_data:
                if job_data.get("started_at"):
                    job_data["started_at"] = datetime.fromisoformat(job_data["started_at"])
                if job_data.get("ended_at"):
                    job_data["ended_at"] = datetime.fromisoformat(job_data["ended_at"])
                jobs.append(JobResponse(**job_data))

        return jobs

    def count_jobs(self) -> int:
        """Get total count of jobs."""
        return len(list(self.jobs_dir.glob("*.json")))

    def update_job_status(
        self,
        job_id: str,
        status: JobStatus,
        **updates,
    ) -> Optional[JobResponse]:
        """
        Update job status and optional fields.

        Args:
            job_id: Job identifier
            status: New job status
            **updates: Additional fields to update

        Returns:
            Updated JobResponse or None if not found
        """
        job_data = self._load_job(job_id)
        if not job_data:
            return None

        job_data["status"] = status.value
        job_data.update(updates)
        job_data["updated_at"] = datetime.utcnow().isoformat()

        self._save_job(job_id, job_data)

        logger.info(f"Job status updated: {job_id} -> {status.value}")

        if job_data.get("started_at"):
            job_data["started_at"] = datetime.fromisoformat(job_data["started_at"])
        if job_data.get("ended_at"):
            job_data["ended_at"] = datetime.fromisoformat(job_data["ended_at"])

        return JobResponse(**job_data)

    def cancel_job(self, job_id: str) -> bool:
        """
        Cancel a job.

        Args:
            job_id: Job identifier

        Returns:
            True if cancelled, False if not found or cannot cancel
        """
        job_data = self._load_job(job_id)
        if not job_data:
            return False

        # Only cancel if pending or running
        current_status = JobStatus(job_data["status"])
        if current_status not in [JobStatus.PENDING, JobStatus.RUNNING]:
            return False

        # Revoke Celery task if exists
        if job_data.get("celery_task_id"):
            celery_app.control.revoke(job_data["celery_task_id"], terminate=True)

        # Update status
        return bool(
            self.update_job_status(
                job_id,
                JobStatus.CANCELLED,
                ended_at=datetime.utcnow().isoformat(),
            )
        )

    def delete_job(self, job_id: str) -> bool:
        """
        Delete a job.

        Args:
            job_id: Job identifier

        Returns:
            True if deleted, False if not found
        """
        job_file = self.jobs_dir / f"{job_id}.json"
        if not job_file.exists():
            return False

        job_file.unlink()
        logger.info(f"Job deleted: {job_id}")
        return True

    def get_job_logs(self, job_id: str) -> list[str]:
        """
        Get logs for a job.

        Args:
            job_id: Job identifier

        Returns:
            List of log lines
        """
        logs_file = settings.results_dir / job_id / "logs.txt"
        if not logs_file.exists():
            return []

        with open(logs_file) as f:
            return f.readlines()

    def _save_job(self, job_id: str, job_data: dict) -> None:
        """Save job data to file."""
        job_file = self.jobs_dir / f"{job_id}.json"
        with open(job_file, "w") as f:
            json.dump(job_data, f, indent=2, default=str)

    def _load_job(self, job_id: str) -> Optional[dict]:
        """Load job data from file."""
        job_file = self.jobs_dir / f"{job_id}.json"
        if not job_file.exists():
            return None

        with open(job_file) as f:
            return json.load(f)

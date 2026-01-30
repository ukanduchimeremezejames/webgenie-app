"""Service layer for results management."""

import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional

from app.core import get_logger, settings
from app.models import ResultResponse, ResultSummary

logger = get_logger(__name__)


class ResultsService:
    """Service for managing inference results."""

    def __init__(self):
        self.results_dir = settings.results_dir
        self.metadata_file = self.results_dir / "results_metadata.json"
        self._load_metadata()

    def _load_metadata(self) -> None:
        """Load results metadata from file."""
        if self.metadata_file.exists():
            with open(self.metadata_file) as f:
                self._metadata = json.load(f)
        else:
            self._metadata = {}

    def _save_metadata(self) -> None:
        """Save results metadata to file."""
        with open(self.metadata_file, "w") as f:
            json.dump(self._metadata, f, indent=2)

    def create_result(
        self,
        job_id: str,
        dataset_id: str,
        algorithm: str,
        summary: Optional[dict] = None,
    ) -> ResultResponse:
        """
        Create a result record.

        Args:
            job_id: Associated job ID
            dataset_id: Associated dataset ID
            algorithm: Algorithm used
            summary: Result summary statistics

        Returns:
            ResultResponse with result details
        """
        result_id = f"result_{uuid.uuid4().hex[:12]}"
        now = datetime.utcnow()

        summary = summary or {}

        metadata = {
            "id": result_id,
            "job_id": job_id,
            "dataset_id": dataset_id,
            "algorithm": algorithm,
            "summary": summary,
            "created_at": now.isoformat(),
            "updated_at": now.isoformat(),
            "output_files": [],
            "size_bytes": 0,
        }

        self._metadata[result_id] = metadata
        self._save_metadata()

        logger.info(f"Result created: {result_id} for job {job_id}")

        return ResultResponse(**metadata)

    def get_result(self, result_id: str) -> Optional[ResultResponse]:
        """
        Get result by ID.

        Args:
            result_id: Result identifier

        Returns:
            ResultResponse or None if not found
        """
        if result_id not in self._metadata:
            return None

        metadata = self._metadata[result_id]
        metadata["created_at"] = datetime.fromisoformat(metadata["created_at"])
        metadata["updated_at"] = datetime.fromisoformat(metadata["updated_at"])

        return ResultResponse(**metadata)

    def get_result_by_job(self, job_id: str) -> Optional[ResultResponse]:
        """
        Get result by job ID.

        Args:
            job_id: Job identifier

        Returns:
            ResultResponse or None if not found
        """
        for result_id, metadata in self._metadata.items():
            if metadata.get("job_id") == job_id:
                metadata["created_at"] = datetime.fromisoformat(metadata["created_at"])
                metadata["updated_at"] = datetime.fromisoformat(metadata["updated_at"])
                return ResultResponse(**metadata)

        return None

    def list_results(
        self,
        dataset_id: Optional[str] = None,
        algorithm: Optional[str] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> list[ResultResponse]:
        """
        List results with optional filtering.

        Args:
            dataset_id: Filter by dataset ID
            algorithm: Filter by algorithm
            skip: Number of records to skip
            limit: Maximum records to return

        Returns:
            List of ResultResponse objects
        """
        results = []
        for metadata in self._metadata.values():
            if dataset_id and metadata.get("dataset_id") != dataset_id:
                continue
            if algorithm and metadata.get("algorithm") != algorithm:
                continue

            metadata["created_at"] = datetime.fromisoformat(metadata["created_at"])
            metadata["updated_at"] = datetime.fromisoformat(metadata["updated_at"])
            results.append(ResultResponse(**metadata))

        # Sort by creation date, newest first
        results.sort(key=lambda r: r.created_at, reverse=True)

        return results[skip : skip + limit]

    def count_results(
        self,
        dataset_id: Optional[str] = None,
        algorithm: Optional[str] = None,
    ) -> int:
        """Get total count of results with optional filtering."""
        count = 0
        for metadata in self._metadata.values():
            if dataset_id and metadata.get("dataset_id") != dataset_id:
                continue
            if algorithm and metadata.get("algorithm") != algorithm:
                continue
            count += 1

        return count

    def update_result(self, result_id: str, updates: dict) -> Optional[ResultResponse]:
        """
        Update result metadata.

        Args:
            result_id: Result identifier
            updates: Dictionary of fields to update

        Returns:
            Updated ResultResponse or None if not found
        """
        if result_id not in self._metadata:
            return None

        metadata = self._metadata[result_id]
        metadata.update(updates)
        metadata["updated_at"] = datetime.utcnow().isoformat()

        self._save_metadata()

        logger.info(f"Result updated: {result_id}")

        metadata["created_at"] = datetime.fromisoformat(metadata["created_at"])
        metadata["updated_at"] = datetime.fromisoformat(metadata["updated_at"])

        return ResultResponse(**metadata)

    def delete_result(self, result_id: str) -> bool:
        """
        Delete a result.

        Args:
            result_id: Result identifier

        Returns:
            True if deleted, False if not found
        """
        if result_id not in self._metadata:
            return False

        del self._metadata[result_id]
        self._save_metadata()

        logger.info(f"Result deleted: {result_id}")
        return True

    def get_result_files(self, result_id: str) -> list[Path]:
        """
        Get list of output files for a result.

        Args:
            result_id: Result identifier

        Returns:
            List of file paths
        """
        job_id = None

        # Find job ID from result metadata
        if result_id in self._metadata:
            job_id = self._metadata[result_id].get("job_id")

        if not job_id:
            return []

        result_dir = self.results_dir / job_id
        if not result_dir.exists():
            return []

        return list(result_dir.glob("*"))

    def get_result_file(self, result_id: str, filename: str) -> Optional[Path]:
        """
        Get a specific output file for a result.

        Args:
            result_id: Result identifier
            filename: Filename to retrieve

        Returns:
            Path to file or None if not found
        """
        job_id = None

        if result_id in self._metadata:
            job_id = self._metadata[result_id].get("job_id")

        if not job_id:
            return None

        file_path = self.results_dir / job_id / filename

        if not file_path.exists():
            return None

        return file_path

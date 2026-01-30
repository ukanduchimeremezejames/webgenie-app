"""Service layer for dataset management."""

import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional

import pandas as pd
from huggingface_hub import dataset_info

from app.core import get_logger, settings
from app.models import DatasetCreate, DatasetResponse, DatasetSchema

logger = get_logger(__name__)


class DatasetsService:
    """Service for managing datasets."""

    def __init__(self):
        self.datasets_dir = settings.datasets_dir
        self.metadata_file = self.datasets_dir / "datasets_metadata.json"
        self._load_metadata()

    def _load_metadata(self) -> None:
        """Load datasets metadata from file."""
        if self.metadata_file.exists():
            with open(self.metadata_file) as f:
                self._metadata = json.load(f)
        else:
            self._metadata = {}

    def _save_metadata(self) -> None:
        """Save datasets metadata to file."""
        with open(self.metadata_file, "w") as f:
            json.dump(self._metadata, f, indent=2)

    def _is_huggingface_dataset(self, file_path: str) -> bool:
        """Check if file_path is a Hugging Face dataset identifier."""
        return "/" in file_path and not file_path.startswith(("/", "\\")) and ":" not in file_path

    def _get_hf_dataset_size(self, hf_dataset_id: str) -> Optional[int]:
        """Get Hugging Face dataset size in bytes."""
        try:
            from huggingface_hub import list_repo_files
            from huggingface_hub import repo_info
            
            # Try to get repo info first
            try:
                info = repo_info(repo_id=hf_dataset_id, repo_type="dataset")
                if hasattr(info, "siblings"):
                    total_size = sum(f.size for f in info.siblings if hasattr(f, "size") and f.size)
                    if total_size > 0:
                        return total_size
            except Exception as repo_error:
                logger.debug(f"Could not get repo info: {repo_error}")
            
            # Fallback: try to list files and sum their sizes
            try:
                files = list_repo_files(repo_id=hf_dataset_id, repo_type="dataset")
                total_size = 0
                for file_info in files:
                    if hasattr(file_info, "size") and file_info.size:
                        total_size += file_info.size
                if total_size > 0:
                    return total_size
            except Exception as list_error:
                logger.debug(f"Could not list repo files: {list_error}")
            
            return None
        except Exception as e:
            logger.warning(f"Could not fetch HF dataset size for {hf_dataset_id}: {e}")
            return None

    def register_dataset(self, dataset_create: DatasetCreate) -> DatasetResponse:
        """
        Register a new dataset.

        Args:
            dataset_create: Dataset creation request

        Returns:
            DatasetResponse with created dataset details

        Raises:
            ValueError: If dataset name already exists or file not found
        """
        # Check if dataset name already exists
        if any(d["name"] == dataset_create.name for d in self._metadata.values()):
            raise ValueError(f"Dataset with name '{dataset_create.name}' already exists")

        # Check if this is a Hugging Face dataset
        is_hf_dataset = self._is_huggingface_dataset(dataset_create.file_path)
        
        if is_hf_dataset:
            # Verify HF dataset exists
            try:
                dataset_info(dataset_create.file_path)
                logger.info(f"Verified Hugging Face dataset: {dataset_create.file_path}")
            except Exception as e:
                raise ValueError(f"Hugging Face dataset not found: {dataset_create.file_path} ({e})")
            size_bytes = self._get_hf_dataset_size(dataset_create.file_path)
        else:
            # Verify local file exists
            file_path = Path(dataset_create.file_path)
            if not file_path.exists():
                raise ValueError(f"File not found: {dataset_create.file_path}")
            size_bytes = file_path.stat().st_size

        # Generate dataset ID
        dataset_id = f"dataset_{uuid.uuid4().hex[:12]}"

        now = datetime.utcnow()

        # Create metadata record
        metadata = {
            "id": dataset_id,
            "name": dataset_create.name,
            "description": dataset_create.description,
            "dataset_type": dataset_create.dataset_type.value,
            "file_path": str(dataset_create.file_path),
            "genes": dataset_create.genes,
            "samples": dataset_create.samples,
            "metadata": dataset_create.metadata or {},
            "created_at": now.isoformat(),
            "updated_at": now.isoformat(),
            "size_bytes": size_bytes,
            "is_hf_dataset": is_hf_dataset,
        }

        self._metadata[dataset_id] = metadata
        self._save_metadata()

        logger.info(f"Dataset registered: {dataset_id} ({dataset_create.name}) [HF: {is_hf_dataset}]")

        return DatasetResponse(**metadata)

    def get_dataset(self, dataset_id: str) -> Optional[DatasetResponse]:
        """
        Get dataset by ID.

        Args:
            dataset_id: Dataset identifier

        Returns:
            DatasetResponse or None if not found
        """
        if dataset_id not in self._metadata:
            return None

        metadata = self._metadata[dataset_id]
        # Convert datetime strings back to datetime objects
        metadata["created_at"] = datetime.fromisoformat(metadata["created_at"])
        metadata["updated_at"] = datetime.fromisoformat(metadata["updated_at"])

        return DatasetResponse(**metadata)

    def list_datasets(self, skip: int = 0, limit: int = 100) -> list[DatasetResponse]:
        """
        List all datasets with pagination.

        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of DatasetResponse objects
        """
        datasets = []
        for metadata in list(self._metadata.values())[skip : skip + limit]:
            metadata["created_at"] = datetime.fromisoformat(metadata["created_at"])
            metadata["updated_at"] = datetime.fromisoformat(metadata["updated_at"])
            datasets.append(DatasetResponse(**metadata))

        return datasets

    def count_datasets(self) -> int:
        """Get total count of datasets."""
        return len(self._metadata)

    def delete_dataset(self, dataset_id: str) -> bool:
        """
        Delete a dataset.

        Args:
            dataset_id: Dataset identifier

        Returns:
            True if deleted, False if not found
        """
        if dataset_id not in self._metadata:
            return False

        del self._metadata[dataset_id]
        self._save_metadata()

        logger.info(f"Dataset deleted: {dataset_id}")
        return True

    def get_dataset_schema(self, dataset_id: str) -> Optional[DatasetSchema]:
        """
        Get schema information for a dataset.

        Args:
            dataset_id: Dataset identifier

        Returns:
            DatasetSchema or None if not found
        """
        dataset = self.get_dataset(dataset_id)
        if not dataset:
            return None

        try:
            # Check if it's a Hugging Face dataset
            is_hf = self._metadata.get(dataset_id, {}).get("is_hf_dataset", False)
            
            if is_hf:
                # For HF datasets, load a sample to get schema
                from datasets import load_dataset
                hf_dataset = load_dataset(dataset.file_path, split="train", streaming=True)
                
                # Get column info from first example
                first_example = next(iter(hf_dataset))
                columns = list(first_example.keys())
                dtypes = {col: type(first_example[col]).__name__ for col in columns}
                
                return DatasetSchema(
                    dataset_id=dataset_id,
                    columns=columns,
                    row_count=None,  # Unknown for streaming datasets
                    column_count=len(columns),
                    dtypes=dtypes,
                )
            else:
                # Read local dataset file to extract schema
                df = pd.read_csv(dataset.file_path, nrows=0)

                return DatasetSchema(
                    dataset_id=dataset_id,
                    columns=df.columns.tolist(),
                    row_count=len(pd.read_csv(dataset.file_path)),
                    column_count=len(df.columns),
                    dtypes={col: str(dtype) for col, dtype in df.dtypes.items()},
                )
        except Exception as e:
            logger.error(f"Failed to read dataset schema: {e}")
            return None

    def update_dataset_metadata(
        self, dataset_id: str, updates: dict
    ) -> Optional[DatasetResponse]:
        """
        Update dataset metadata.

        Args:
            dataset_id: Dataset identifier
            updates: Dictionary of fields to update

        Returns:
            Updated DatasetResponse or None if not found
        """
        if dataset_id not in self._metadata:
            return None

        metadata = self._metadata[dataset_id]
        metadata.update(updates)
        metadata["updated_at"] = datetime.utcnow().isoformat()

        self._save_metadata()

        logger.info(f"Dataset metadata updated: {dataset_id}")

        metadata["created_at"] = datetime.fromisoformat(metadata["created_at"])
        metadata["updated_at"] = datetime.fromisoformat(metadata["updated_at"])

        return DatasetResponse(**metadata)

"""Pytest configuration and shared fixtures."""

import pytest
from pathlib import Path
import tempfile
import json

from app.core import settings
from app.services.datasets_service import DatasetsService
from app.services.jobs_service import JobsService
from app.services.inference_service import ResultsService


@pytest.fixture
def temp_data_dir():
    """Create temporary data directory for tests."""
    with tempfile.TemporaryDirectory() as tmpdir:
        original_data_dir = settings.data_dir
        original_datasets_dir = settings.datasets_dir
        original_results_dir = settings.results_dir

        settings.data_dir = Path(tmpdir)
        settings.datasets_dir = Path(tmpdir) / "datasets"
        settings.results_dir = Path(tmpdir) / "results"

        settings.data_dir.mkdir(parents=True, exist_ok=True)
        settings.datasets_dir.mkdir(parents=True, exist_ok=True)
        settings.results_dir.mkdir(parents=True, exist_ok=True)

        yield Path(tmpdir)

        # Restore original settings
        settings.data_dir = original_data_dir
        settings.datasets_dir = original_datasets_dir
        settings.results_dir = original_results_dir


@pytest.fixture
def datasets_service(temp_data_dir):
    """Create datasets service instance."""
    return DatasetsService()


@pytest.fixture
def jobs_service(temp_data_dir):
    """Create jobs service instance."""
    return JobsService()


@pytest.fixture
def results_service(temp_data_dir):
    """Create results service instance."""
    return ResultsService()


@pytest.fixture
def sample_dataset_file(temp_data_dir):
    """Create a sample dataset file for testing."""
    import pandas as pd
    import numpy as np

    # Create sample data
    n_genes = 100
    n_samples = 50

    data = np.random.randn(n_genes, n_samples)
    df = pd.DataFrame(
        data,
        index=[f"GENE_{i}" for i in range(n_genes)],
        columns=[f"SAMPLE_{i}" for i in range(n_samples)],
    )

    # Save to file
    file_path = temp_data_dir / "sample_dataset.csv"
    df.to_csv(file_path)

    return str(file_path)

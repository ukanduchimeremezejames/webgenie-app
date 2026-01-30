"""Integration tests for API endpoints."""

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.models import DatasetCreate, DatasetType, JobCreate


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


def test_root_endpoint(client):
    """Test root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    assert "version" in response.json()


def test_health_endpoint(client):
    """Test health endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_register_dataset(client, sample_dataset_file):
    """Test dataset registration endpoint."""
    dataset_data = {
        "name": "test_dataset",
        "description": "Test dataset",
        "dataset_type": "expression",
        "file_path": sample_dataset_file,
        "genes": 100,
        "samples": 50,
    }

    response = client.post("/api/datasets/", json=dataset_data)

    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "test_dataset"
    assert "id" in data


def test_list_datasets(client, sample_dataset_file):
    """Test list datasets endpoint."""
    # Register a dataset first
    dataset_data = {
        "name": "test_dataset",
        "dataset_type": "expression",
        "file_path": sample_dataset_file,
    }

    client.post("/api/datasets/", json=dataset_data)

    # List datasets
    response = client.get("/api/datasets/")

    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 1
    assert len(data["datasets"]) >= 1


def test_get_dataset(client, sample_dataset_file):
    """Test get dataset endpoint."""
    # Register a dataset
    dataset_data = {
        "name": "test_dataset",
        "dataset_type": "expression",
        "file_path": sample_dataset_file,
    }

    register_response = client.post("/api/datasets/", json=dataset_data)
    dataset_id = register_response.json()["id"]

    # Get dataset
    response = client.get(f"/api/datasets/{dataset_id}")

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == dataset_id


def test_get_dataset_schema(client, sample_dataset_file):
    """Test get dataset schema endpoint."""
    # Register a dataset
    dataset_data = {
        "name": "test_dataset",
        "dataset_type": "expression",
        "file_path": sample_dataset_file,
    }

    register_response = client.post("/api/datasets/", json=dataset_data)
    dataset_id = register_response.json()["id"]

    # Get schema
    response = client.get(f"/api/datasets/{dataset_id}/schema")

    assert response.status_code == 200
    data = response.json()
    assert "columns" in data
    assert "row_count" in data
    assert "column_count" in data


@pytest.mark.asyncio
async def test_submit_job(client, sample_dataset_file):
    """Test submit job endpoint."""
    # Register a dataset first
    dataset_data = {
        "name": "test_dataset",
        "dataset_type": "expression",
        "file_path": sample_dataset_file,
    }

    dataset_response = client.post("/api/datasets/", json=dataset_data)
    dataset_id = dataset_response.json()["id"]

    # Submit job
    job_data = {
        "dataset_id": dataset_id,
        "algorithm": "GRNBoost2",
        "params": {"n_jobs": 4},
    }

    response = client.post("/api/jobs/", json=job_data)

    assert response.status_code == 201
    data = response.json()
    assert data["status"] == "pending"
    assert data["algorithm"] == "GRNBoost2"


@pytest.mark.asyncio
async def test_list_jobs(client, sample_dataset_file):
    """Test list jobs endpoint."""
    response = client.get("/api/jobs/")

    assert response.status_code == 200
    data = response.json()
    assert "total" in data
    assert "jobs" in data


@pytest.mark.asyncio
async def test_list_results(client):
    """Test list results endpoint."""
    response = client.get("/api/results/")

    assert response.status_code == 200
    data = response.json()
    assert "total" in data
    assert "results" in data

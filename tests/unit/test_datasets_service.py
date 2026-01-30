"""Unit tests for datasets service."""

import pytest
from app.models import DatasetCreate, DatasetType


def test_register_dataset(datasets_service, sample_dataset_file):
    """Test registering a new dataset."""
    dataset_create = DatasetCreate(
        name="test_dataset",
        description="Test dataset",
        dataset_type=DatasetType.EXPRESSION,
        file_path=sample_dataset_file,
        genes=100,
        samples=50,
    )

    result = datasets_service.register_dataset(dataset_create)

    assert result.name == "test_dataset"
    assert result.dataset_type == DatasetType.EXPRESSION
    assert result.genes == 100
    assert result.samples == 50


def test_register_duplicate_dataset(datasets_service, sample_dataset_file):
    """Test registering duplicate dataset raises error."""
    dataset_create = DatasetCreate(
        name="test_dataset",
        description="Test dataset",
        dataset_type=DatasetType.EXPRESSION,
        file_path=sample_dataset_file,
    )

    datasets_service.register_dataset(dataset_create)

    with pytest.raises(ValueError, match="already exists"):
        datasets_service.register_dataset(dataset_create)


def test_get_dataset(datasets_service, sample_dataset_file):
    """Test retrieving a dataset."""
    dataset_create = DatasetCreate(
        name="test_dataset",
        description="Test dataset",
        dataset_type=DatasetType.EXPRESSION,
        file_path=sample_dataset_file,
    )

    created = datasets_service.register_dataset(dataset_create)
    retrieved = datasets_service.get_dataset(created.id)

    assert retrieved is not None
    assert retrieved.name == "test_dataset"
    assert retrieved.id == created.id


def test_list_datasets(datasets_service, sample_dataset_file):
    """Test listing datasets."""
    for i in range(3):
        dataset_create = DatasetCreate(
            name=f"test_dataset_{i}",
            dataset_type=DatasetType.EXPRESSION,
            file_path=sample_dataset_file,
        )
        datasets_service.register_dataset(dataset_create)

    datasets = datasets_service.list_datasets()

    assert len(datasets) == 3
    assert datasets_service.count_datasets() == 3


def test_delete_dataset(datasets_service, sample_dataset_file):
    """Test deleting a dataset."""
    dataset_create = DatasetCreate(
        name="test_dataset",
        dataset_type=DatasetType.EXPRESSION,
        file_path=sample_dataset_file,
    )

    created = datasets_service.register_dataset(dataset_create)
    success = datasets_service.delete_dataset(created.id)

    assert success is True
    assert datasets_service.get_dataset(created.id) is None


def test_get_dataset_schema(datasets_service, sample_dataset_file):
    """Test retrieving dataset schema."""
    dataset_create = DatasetCreate(
        name="test_dataset",
        dataset_type=DatasetType.EXPRESSION,
        file_path=sample_dataset_file,
    )

    created = datasets_service.register_dataset(dataset_create)
    schema = datasets_service.get_dataset_schema(created.id)

    assert schema is not None
    assert schema.row_count == 100
    assert schema.column_count == 50
    assert len(schema.columns) == 50

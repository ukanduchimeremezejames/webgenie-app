"""Beeline GRNBoost2 algorithm runner."""

import logging
import tempfile
from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd

from app.core import settings
from app.services.runners.utils import log_step, save_result, validate_params

logger = logging.getLogger(__name__)


def _is_huggingface_dataset(path: str) -> bool:
    """Check if path is a HuggingFace dataset identifier."""
    return "/" in path and not path.startswith(("/", "\\")) and ":" not in path


def _load_dataset(dataset_path: str, job_logger) -> pd.DataFrame:
    """
    Load dataset from either local file or HuggingFace Hub.
    
    Args:
        dataset_path: Path to dataset (local or HF ID like 'owner/dataset')
        job_logger: Logger instance
        
    Returns:
        Loaded dataset as pandas DataFrame
    """
    if _is_huggingface_dataset(dataset_path):
        # Load from HuggingFace Hub
        log_step(job_logger, "Loading HF dataset", dataset_path)
        try:
            from datasets import load_dataset
            
            # Load the dataset from HuggingFace
            hf_dataset = load_dataset(dataset_path, split="train", streaming=False)
            
            # Convert to pandas DataFrame
            df = hf_dataset.to_pandas()
            
            # Ensure genes (rows) are indexed
            if df.index.name is None:
                df = df.set_index(df.columns[0]) if len(df.columns) > 0 else df
                
            log_step(job_logger, "HF dataset loaded", f"Shape: {df.shape}")
            return df
            
        except Exception as e:
            raise ValueError(f"Failed to load HuggingFace dataset '{dataset_path}': {e}")
    else:
        # Load from local file
        log_step(job_logger, "Loading local dataset", dataset_path)
        if not Path(dataset_path).exists():
            raise FileNotFoundError(f"Dataset not found: {dataset_path}")
        
        df = pd.read_csv(dataset_path, index_col=0)
        log_step(job_logger, "Local dataset loaded", f"Shape: {df.shape}")
        return df


def run_beeline_pipeline(
    dataset_path: str,
    algorithm: str,
    params: dict,
    output_dir: Optional[Path] = None,
    job_id: Optional[str] = None,
) -> dict:
    """
    Execute Beeline GRN inference pipeline.

    Args:
        dataset_path: Path to input dataset (CSV or HF dataset ID)
        algorithm: Algorithm name (GRNBoost2, SCENIC, PIDC, etc.)
        params: Algorithm-specific parameters
        output_dir: Output directory for results
        job_id: Job ID for logging context

    Returns:
        Dictionary with execution results and metadata
    """
    if job_id:
        logger.info(f"Starting Beeline pipeline for job {job_id}")

    # Setup logging context
    job_logger = logging.getLogger(f"beeline.{job_id}") if job_id else logger

    # Validate algorithm
    if algorithm not in settings.supported_algorithms:
        raise ValueError(
            f"Algorithm '{algorithm}' not supported. "
            f"Supported: {', '.join(settings.supported_algorithms)}"
        )

    # Set default output directory
    if output_dir is None:
        if job_id:
            output_dir = settings.results_dir / job_id
        else:
            output_dir = Path(tempfile.mkdtemp())

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    log_step(job_logger, "Initialization", f"Algorithm: {algorithm}")

    try:
        # Load dataset (handles both local and HF datasets)
        log_step(job_logger, "Loading dataset", dataset_path)
        df = _load_dataset(dataset_path, job_logger)
        genes = df.shape[0]
        samples = df.shape[1]

        log_step(job_logger, "Dataset loaded", f"{genes} genes x {samples} samples")

        # Route to algorithm-specific implementation
        if algorithm == "GRNBoost2":
            result = _run_grn_boost2(df, params, output_dir, job_logger)
        elif algorithm == "SCENIC":
            result = _run_scenic(df, params, output_dir, job_logger)
        elif algorithm == "PIDC":
            result = _run_pidc(df, params, output_dir, job_logger)
        elif algorithm == "CLR":
            result = _run_clr(df, params, output_dir, job_logger)
        elif algorithm == "ARACNE":
            result = _run_aracne(df, params, output_dir, job_logger)
        elif algorithm == "NES":
            result = _run_nes(df, params, output_dir, job_logger)
        elif algorithm == "Inferelator":
            result = _run_inferelator(df, params, output_dir, job_logger)
        elif algorithm == "pySCENIC":
            result = _run_pyscenic(df, params, output_dir, job_logger)
        else:
            raise ValueError(f"Algorithm implementation not found: {algorithm}")

        # Add metadata
        result["status"] = "completed"
        result["algorithm"] = algorithm
        result["output_dir"] = str(output_dir)

        log_step(job_logger, "Pipeline completed", f"Edges: {result.get('edges_count', 0)}")

        # Save result metadata
        save_result(output_dir, result, "metadata.json")

        return result

    except Exception as e:
        job_logger.error(f"Pipeline failed: {str(e)}")
        error_result = {
            "status": "failed",
            "algorithm": algorithm,
            "error": str(e),
            "output_dir": str(output_dir),
        }
        save_result(output_dir, error_result, "metadata.json")
        raise


def _run_grn_boost2(
    data: pd.DataFrame,
    params: dict,
    output_dir: Path,
    logger_instance: logging.Logger,
) -> dict:
    """Execute GRNBoost2 algorithm."""
    log_step(logger_instance, "GRNBoost2", "Initializing")

    # Default parameters
    defaults = {
        "n_jobs": 4,
        "early_stopping": True,
        "verbose": 0,
    }
    validated_params = validate_params(params, [], defaults)

    try:
        # Try to import GRNBoost2
        try:
            from arboretum.core import GRNBoost2 as GRNBoost2Impl
        except ImportError:
            logger_instance.warning("arboretum not installed, using mock implementation")
            # Use mock implementation if not available
            return _mock_grn_inference(data, output_dir, logger_instance, "GRNBoost2")

        log_step(logger_instance, "GRNBoost2", "Training model")

        # Initialize and run GRNBoost2
        model = GRNBoost2Impl(n_jobs=validated_params["n_jobs"])
        adjacency = model.fit(data.T).predict(data.T)

        # Process results
        adjacency_df = pd.DataFrame(
            adjacency,
            index=data.index,
            columns=data.index,
        )

        # Save adjacency matrix
        adj_path = output_dir / "adjacency_matrix.csv"
        adjacency_df.to_csv(adj_path)
        log_step(logger_instance, "Results saved", str(adj_path))

        # Calculate statistics
        edges = (adjacency_df > 0).sum().sum()
        weights = adjacency_df.values[adjacency_df.values > 0]

        return {
            "edges_count": int(edges),
            "mean_weight": float(np.mean(weights)) if len(weights) > 0 else 0.0,
            "max_weight": float(np.max(weights)) if len(weights) > 0 else 0.0,
            "min_weight": float(np.min(weights)) if len(weights) > 0 else 0.0,
            "output_files": ["adjacency_matrix.csv"],
        }

    except Exception as e:
        logger_instance.error(f"GRNBoost2 execution failed: {e}")
        raise


def _run_scenic(
    data: pd.DataFrame,
    params: dict,
    output_dir: Path,
    logger_instance: logging.Logger,
) -> dict:
    """Execute SCENIC algorithm."""
    log_step(logger_instance, "SCENIC", "Initializing")

    try:
        from pyscenic.inference import grnboost2

        log_step(logger_instance, "SCENIC", "Running motif inference")

        # Run pySCENIC (simplified version)
        adjacency = grnboost2(data.T, verbose=False)

        # Save results
        adj_path = output_dir / "scenic_adjacency.csv"
        adjacency.to_csv(adj_path)

        edges = (adjacency > 0).sum().sum()
        return {
            "edges_count": int(edges),
            "output_files": ["scenic_adjacency.csv"],
        }

    except ImportError:
        logger_instance.warning("pySCENIC not installed, using mock implementation")
        return _mock_grn_inference(data, output_dir, logger_instance, "SCENIC")


def _run_pidc(
    data: pd.DataFrame,
    params: dict,
    output_dir: Path,
    logger_instance: logging.Logger,
) -> dict:
    """Execute PIDC algorithm."""
    log_step(logger_instance, "PIDC", "Mock implementation")
    return _mock_grn_inference(data, output_dir, logger_instance, "PIDC")


def _run_clr(
    data: pd.DataFrame,
    params: dict,
    output_dir: Path,
    logger_instance: logging.Logger,
) -> dict:
    """Execute CLR algorithm."""
    log_step(logger_instance, "CLR", "Mock implementation")
    return _mock_grn_inference(data, output_dir, logger_instance, "CLR")


def _run_aracne(
    data: pd.DataFrame,
    params: dict,
    output_dir: Path,
    logger_instance: logging.Logger,
) -> dict:
    """Execute ARACNE algorithm."""
    log_step(logger_instance, "ARACNE", "Mock implementation")
    return _mock_grn_inference(data, output_dir, logger_instance, "ARACNE")


def _run_nes(
    data: pd.DataFrame,
    params: dict,
    output_dir: Path,
    logger_instance: logging.Logger,
) -> dict:
    """Execute NES algorithm."""
    log_step(logger_instance, "NES", "Mock implementation")
    return _mock_grn_inference(data, output_dir, logger_instance, "NES")


def _run_inferelator(
    data: pd.DataFrame,
    params: dict,
    output_dir: Path,
    logger_instance: logging.Logger,
) -> dict:
    """Execute Inferelator algorithm."""
    log_step(logger_instance, "Inferelator", "Mock implementation")
    return _mock_grn_inference(data, output_dir, logger_instance, "Inferelator")


def _run_pyscenic(
    data: pd.DataFrame,
    params: dict,
    output_dir: Path,
    logger_instance: logging.Logger,
) -> dict:
    """Execute pySCENIC algorithm."""
    log_step(logger_instance, "pySCENIC", "Mock implementation")
    return _mock_grn_inference(data, output_dir, logger_instance, "pySCENIC")


def _mock_grn_inference(
    data: pd.DataFrame,
    output_dir: Path,
    logger_instance: logging.Logger,
    algorithm: str,
) -> dict:
    """
    Generate mock GRN inference results for testing/demo purposes.

    This creates a sparse adjacency matrix with realistic statistics.
    """
    log_step(logger_instance, "Generating mock results", algorithm)

    n_genes = data.shape[0]

    # Generate sparse random adjacency matrix (similar to real GRN)
    np.random.seed(42)
    sparsity = 0.95  # 95% sparse (realistic for biological networks)
    adjacency = np.random.rand(n_genes, n_genes)
    adjacency[adjacency > (1 - sparsity)] = 0
    adjacency = adjacency * (1 - np.eye(n_genes))  # Remove self-loops

    adjacency_df = pd.DataFrame(
        adjacency,
        index=data.index,
        columns=data.index,
    )

    # Save adjacency matrix
    adj_path = output_dir / "adjacency_matrix.csv"
    adjacency_df.to_csv(adj_path)

    # Calculate statistics
    edges = (adjacency_df > 0).sum().sum()
    weights = adjacency_df.values[adjacency_df.values > 0]

    log_step(logger_instance, "Mock results ready", f"Edges: {edges}")

    return {
        "edges_count": int(edges),
        "mean_weight": float(np.mean(weights)) if len(weights) > 0 else 0.0,
        "max_weight": float(np.max(weights)) if len(weights) > 0 else 0.0,
        "min_weight": float(np.min(weights)) if len(weights) > 0 else 0.0,
        "output_files": ["adjacency_matrix.csv"],
        "note": "Mock implementation - for testing/demo purposes",
    }

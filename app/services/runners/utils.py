"""Utility functions for runners."""

import json
import logging
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

logger = logging.getLogger(__name__)


def run_command(
    cmd: list[str],
    cwd: Optional[Path] = None,
    timeout: int = 3600,
    env: Optional[dict] = None,
) -> tuple[int, str, str]:
    """
    Execute a shell command safely.

    Args:
        cmd: Command and arguments as list
        cwd: Working directory
        timeout: Timeout in seconds
        env: Environment variables

    Returns:
        Tuple of (return_code, stdout, stderr)
    """
    try:
        result = subprocess.run(
            cmd,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=timeout,
            env=env,
        )
        return result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        logger.error(f"Command timed out after {timeout}s: {' '.join(cmd)}")
        return 124, "", f"Command timed out after {timeout}s"
    except Exception as e:
        logger.error(f"Command execution failed: {e}")
        return 1, "", str(e)


def save_result(output_dir: Path, result_data: dict, filename: str = "result.json") -> Path:
    """
    Save result data to JSON file.

    Args:
        output_dir: Output directory
        result_data: Result dictionary
        filename: Output filename

    Returns:
        Path to saved file
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / filename

    with open(output_path, "w") as f:
        json.dump(result_data, f, indent=2)

    logger.info(f"Result saved to {output_path}")
    return output_path


def log_step(logger_instance: logging.Logger, step: str, details: Optional[str] = None) -> None:
    """Log a step in algorithm execution."""
    timestamp = datetime.utcnow().isoformat()
    message = f"[{timestamp}] {step}"
    if details:
        message += f": {details}"
    logger_instance.info(message)


def validate_params(params: dict, required: list[str], defaults: Optional[dict] = None) -> dict:
    """
    Validate and merge parameters with defaults.

    Args:
        params: Provided parameters
        required: List of required parameter names
        defaults: Default values for parameters

    Returns:
        Merged parameters dictionary

    Raises:
        ValueError: If required parameters are missing
    """
    merged = defaults.copy() if defaults else {}
    merged.update(params)

    missing = [p for p in required if p not in merged]
    if missing:
        raise ValueError(f"Missing required parameters: {missing}")

    return merged

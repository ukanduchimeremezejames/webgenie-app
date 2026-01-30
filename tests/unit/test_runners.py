"""Unit tests for runner utilities."""

import pytest
import logging
from app.services.runners.utils import validate_params, log_step


def test_validate_params_with_defaults():
    """Test parameter validation with defaults."""
    params = {"a": 1}
    defaults = {"b": 2, "c": 3}
    required = ["a"]

    result = validate_params(params, required, defaults)

    assert result == {"a": 1, "b": 2, "c": 3}


def test_validate_params_missing_required():
    """Test parameter validation with missing required params."""
    params = {}
    required = ["a", "b"]

    with pytest.raises(ValueError, match="Missing required parameters"):
        validate_params(params, required)


def test_log_step(caplog):
    """Test log step utility."""
    logger = logging.getLogger("test")

    with caplog.at_level(logging.INFO):
        log_step(logger, "test_step", "test_details")

    assert "test_step" in caplog.text
    assert "test_details" in caplog.text

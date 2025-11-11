"""Basic tests for aurea-orchestrator."""

import aurea_orchestrator


def test_version():
    """Test that version is defined."""
    assert aurea_orchestrator.__version__ == "0.1.0"


def test_import():
    """Test that package can be imported."""
    assert aurea_orchestrator is not None

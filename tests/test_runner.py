"""Unit tests for the sandbox runner."""

import pytest
from unittest.mock import Mock, patch, MagicMock
from src.sandbox.runner import SandboxRunner


class TestSandboxRunner:
    """Test cases for SandboxRunner."""
    
    def test_get_code_filename_python(self):
        """Test getting code filename for Python."""
        runner = SandboxRunner()
        assert runner._get_code_filename("python") == "main.py"
    
    def test_get_code_filename_javascript(self):
        """Test getting code filename for JavaScript."""
        runner = SandboxRunner()
        assert runner._get_code_filename("javascript") == "main.js"
    
    def test_get_code_filename_unknown(self):
        """Test getting code filename for unknown language."""
        runner = SandboxRunner()
        assert runner._get_code_filename("unknown") == "main.txt"
    
    def test_get_execution_command_python(self):
        """Test getting execution command for Python."""
        runner = SandboxRunner()
        cmd = runner._get_execution_command("python", "main.py")
        assert cmd == ["python3", "main.py"]
    
    def test_get_execution_command_javascript(self):
        """Test getting execution command for JavaScript."""
        runner = SandboxRunner()
        cmd = runner._get_execution_command("javascript", "main.js")
        assert cmd == ["node", "main.js"]
    
    def test_initialization_defaults(self):
        """Test SandboxRunner initialization with defaults."""
        runner = SandboxRunner()
        assert runner.image == "aurea-sandbox:latest"
        assert runner.cpu_limit == 1.0
        assert runner.memory_limit == "512m"
        assert runner.default_timeout == 30
    
    def test_initialization_custom(self):
        """Test SandboxRunner initialization with custom values."""
        runner = SandboxRunner(
            image="custom:tag",
            cpu_limit=2.0,
            memory_limit="1g",
            default_timeout=60
        )
        assert runner.image == "custom:tag"
        assert runner.cpu_limit == 2.0
        assert runner.memory_limit == "1g"
        assert runner.default_timeout == 60


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

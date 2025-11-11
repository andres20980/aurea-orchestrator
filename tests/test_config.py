"""Tests for configuration."""

import os
import pytest
from aurea.config import Config


class TestConfig:
    """Test configuration functionality."""
    
    def test_default_values(self):
        """Test default configuration values."""
        config = Config()
        assert config.MAX_JOB_COST == 10.0
        assert config.DEFAULT_RPM == 60
        assert config.DEFAULT_TPM == 100000
        assert config.MAX_RETRIES == 3
        assert config.CIRCUIT_BREAKER_THRESHOLD == 5
    
    def test_custom_values(self):
        """Test custom configuration values."""
        config = Config(
            MAX_JOB_COST=20.0,
            DEFAULT_RPM=120,
            MAX_RETRIES=5
        )
        assert config.MAX_JOB_COST == 20.0
        assert config.DEFAULT_RPM == 120
        assert config.MAX_RETRIES == 5
    
    def test_is_model_allowed_no_restrictions(self):
        """Test model allowance with no restrictions."""
        config = Config()
        assert config.is_model_allowed("gpt-4") is True
        assert config.is_model_allowed("claude-3") is True
        assert config.is_model_allowed("any-model") is True
    
    def test_is_model_allowed_with_allow_list(self):
        """Test model allowance with allow list."""
        config = Config(ALLOWED_MODELS=["gpt-4", "gpt-3.5-turbo"])
        assert config.is_model_allowed("gpt-4") is True
        assert config.is_model_allowed("gpt-3.5-turbo") is True
        assert config.is_model_allowed("claude-3") is False
    
    def test_is_model_allowed_with_deny_list(self):
        """Test model allowance with deny list."""
        config = Config(DENIED_MODELS=["bad-model"])
        assert config.is_model_allowed("gpt-4") is True
        assert config.is_model_allowed("bad-model") is False
    
    def test_deny_list_takes_precedence(self):
        """Test that deny list takes precedence over allow list."""
        config = Config(
            ALLOWED_MODELS=["gpt-4", "claude-3"],
            DENIED_MODELS=["claude-3"]
        )
        assert config.is_model_allowed("gpt-4") is True
        assert config.is_model_allowed("claude-3") is False
    
    def test_redact_pii_default(self):
        """Test PII redaction default setting."""
        config = Config()
        assert config.REDACT_PII is True
    
    def test_log_level_default(self):
        """Test log level default."""
        config = Config()
        assert config.LOG_LEVEL == "INFO"

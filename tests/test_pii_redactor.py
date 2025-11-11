"""Tests for PII redactor."""

import pytest
from aurea.pii_redactor import PIIRedactor


class TestPIIRedactor:
    """Test PII redaction functionality."""
    
    def test_redact_email(self):
        """Test email redaction."""
        text = "Contact me at user@example.com for details"
        redacted = PIIRedactor.redact(text)
        assert "user@example.com" not in redacted
        assert "[EMAIL_REDACTED]" in redacted
    
    def test_redact_phone(self):
        """Test phone number redaction."""
        text = "Call me at 555-123-4567 or (555) 123-4567"
        redacted = PIIRedactor.redact(text)
        assert "555-123-4567" not in redacted
        assert "[PHONE_REDACTED]" in redacted
    
    def test_redact_ssn(self):
        """Test SSN redaction."""
        text = "My SSN is 123-45-6789"
        redacted = PIIRedactor.redact(text)
        assert "123-45-6789" not in redacted
        assert "[SSN_REDACTED]" in redacted
    
    def test_redact_credit_card(self):
        """Test credit card redaction."""
        text = "Card number: 1234-5678-9012-3456"
        redacted = PIIRedactor.redact(text)
        assert "1234-5678-9012-3456" not in redacted
        assert "[CARD_REDACTED]" in redacted
    
    def test_redact_ip_address(self):
        """Test IP address redaction."""
        text = "Server at 192.168.1.1 is down"
        redacted = PIIRedactor.redact(text)
        assert "192.168.1.1" not in redacted
        assert "[IP_REDACTED]" in redacted
    
    def test_redact_api_key(self):
        """Test API key redaction."""
        text = "API key: a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6"
        redacted = PIIRedactor.redact(text)
        assert "a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6" not in redacted
        assert "[KEY_REDACTED]" in redacted
    
    def test_redact_bearer_token(self):
        """Test bearer token redaction."""
        text = "Authorization: Bearer abc123xyz456"
        redacted = PIIRedactor.redact(text)
        assert "abc123xyz456" not in redacted
        assert "[TOKEN_REDACTED]" in redacted
    
    def test_redact_dict_simple(self):
        """Test dictionary redaction."""
        data = {
            "email": "user@example.com",
            "phone": "555-123-4567",
            "message": "Hello world"
        }
        redacted = PIIRedactor.redact_dict(data)
        
        assert "[EMAIL_REDACTED]" in redacted["email"]
        assert "[PHONE_REDACTED]" in redacted["phone"]
        assert redacted["message"] == "Hello world"
    
    def test_redact_dict_sensitive_keys(self):
        """Test that sensitive keys are fully redacted."""
        data = {
            "password": "secret123",
            "api_key": "mykey123",
            "token": "abc123",
            "secret": "topsecret"
        }
        redacted = PIIRedactor.redact_dict(data)
        
        assert redacted["password"] == "[REDACTED]"
        assert redacted["api_key"] == "[REDACTED]"
        assert redacted["token"] == "[REDACTED]"
        assert redacted["secret"] == "[REDACTED]"
    
    def test_redact_dict_nested(self):
        """Test nested dictionary redaction."""
        data = {
            "user": {
                "email": "user@example.com",
                "password": "secret",
                "name": "John Doe"
            },
            "message": "Call me at 555-123-4567"
        }
        redacted = PIIRedactor.redact_dict(data)
        
        assert "[EMAIL_REDACTED]" in redacted["user"]["email"]
        assert redacted["user"]["password"] == "[REDACTED]"
        assert redacted["user"]["name"] == "John Doe"
        assert "[PHONE_REDACTED]" in redacted["message"]
    
    def test_redact_dict_with_list(self):
        """Test dictionary with list redaction."""
        data = {
            "emails": ["user1@example.com", "user2@example.com"],
            "messages": ["Hello", "My SSN is 123-45-6789"]
        }
        redacted = PIIRedactor.redact_dict(data)
        
        assert "[EMAIL_REDACTED]" in redacted["emails"][0]
        assert "[EMAIL_REDACTED]" in redacted["emails"][1]
        assert redacted["messages"][0] == "Hello"
        assert "[SSN_REDACTED]" in redacted["messages"][1]
    
    def test_non_string_input(self):
        """Test that non-string inputs are handled gracefully."""
        assert PIIRedactor.redact(123) == 123
        assert PIIRedactor.redact(None) is None
        assert PIIRedactor.redact([1, 2, 3]) == [1, 2, 3]

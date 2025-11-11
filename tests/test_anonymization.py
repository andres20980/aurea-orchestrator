"""
Tests for anonymization service
"""
import pytest
from app.services.anonymization import AnonymizationService


@pytest.fixture
def anonymizer():
    return AnonymizationService()


def test_anonymize_email(anonymizer):
    """Test email anonymization"""
    email = "john.doe@example.com"
    result = anonymizer.anonymize_email(email)
    
    assert result != email
    assert "@" in result
    assert "example.com" in result or "***" in result
    assert result[0] == 'j'  # First letter preserved


def test_anonymize_name(anonymizer):
    """Test name anonymization"""
    name = "John Smith"
    result = anonymizer.anonymize_name(name)
    
    assert result != name
    assert "J." in result
    assert "S." in result


def test_anonymize_phone(anonymizer):
    """Test phone number anonymization"""
    phone = "555-123-4567"
    result = anonymizer.anonymize_phone(phone)
    
    assert result != phone
    assert "4567" in result  # Last 4 digits preserved
    assert "***" in result


def test_anonymize_ssn(anonymizer):
    """Test SSN anonymization"""
    ssn = "123-45-6789"
    result = anonymizer.anonymize_ssn(ssn)
    
    assert result != ssn
    assert "6789" in result
    assert "***-**-" in result


def test_anonymize_address(anonymizer):
    """Test address anonymization"""
    address = "123 Main St, Springfield, IL"
    result = anonymizer.anonymize_address(address)
    
    assert result != address
    assert "***" in result


def test_encrypt_decrypt(anonymizer):
    """Test encryption and decryption"""
    original = "sensitive data"
    encrypted = anonymizer.encrypt_data(original)
    decrypted = anonymizer.decrypt_data(encrypted)
    
    assert encrypted != original
    assert decrypted == original


def test_anonymize_dict(anonymizer):
    """Test dictionary anonymization"""
    data = {
        "email": "test@example.com",
        "name": "John Doe",
        "phone": "555-1234",
        "other": "not sensitive"
    }
    
    result = anonymizer.anonymize_dict(data, ["email", "name", "phone"])
    
    assert result["email"] != data["email"]
    assert result["name"] != data["name"]
    assert result["phone"] != data["phone"]
    assert result["other"] == data["other"]

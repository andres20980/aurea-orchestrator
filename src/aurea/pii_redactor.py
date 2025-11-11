"""PII redaction utilities for secure logging."""

import re
from typing import Any, Dict


class PIIRedactor:
    """Redacts Personally Identifiable Information from logs."""
    
    # Common PII patterns
    PATTERNS = {
        'email': re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'),
        'phone': re.compile(r'\b(?:\+?1[-.]?)?\(?\d{3}\)?[-.]?\d{3}[-.]?\d{4}\b'),
        'ssn': re.compile(r'\b\d{3}-\d{2}-\d{4}\b'),
        'credit_card': re.compile(r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b'),
        'ip_address': re.compile(r'\b(?:\d{1,3}\.){3}\d{1,3}\b'),
        'api_key': re.compile(r'\b[A-Za-z0-9]{32,}\b'),
        'bearer_token': re.compile(r'Bearer\s+[A-Za-z0-9\-._~+/]+=*', re.IGNORECASE),
        'authorization': re.compile(r'Authorization:\s*[^\s]+', re.IGNORECASE),
    }
    
    @classmethod
    def redact(cls, text: str) -> str:
        """Redact PII from a text string."""
        if not isinstance(text, str):
            return text
        
        redacted = text
        for pii_type, pattern in cls.PATTERNS.items():
            if pii_type in ('email',):
                redacted = pattern.sub('[EMAIL_REDACTED]', redacted)
            elif pii_type in ('phone',):
                redacted = pattern.sub('[PHONE_REDACTED]', redacted)
            elif pii_type in ('ssn',):
                redacted = pattern.sub('[SSN_REDACTED]', redacted)
            elif pii_type in ('credit_card',):
                redacted = pattern.sub('[CARD_REDACTED]', redacted)
            elif pii_type in ('ip_address',):
                redacted = pattern.sub('[IP_REDACTED]', redacted)
            elif pii_type in ('api_key',):
                redacted = pattern.sub('[KEY_REDACTED]', redacted)
            elif pii_type in ('bearer_token',):
                redacted = pattern.sub('Bearer [TOKEN_REDACTED]', redacted)
            elif pii_type in ('authorization',):
                redacted = pattern.sub('Authorization: [AUTH_REDACTED]', redacted)
        
        return redacted
    
    @classmethod
    def redact_dict(cls, data: Dict[str, Any]) -> Dict[str, Any]:
        """Recursively redact PII from a dictionary."""
        if not isinstance(data, dict):
            return data
        
        redacted = {}
        for key, value in data.items():
            # Redact sensitive keys entirely
            if key.lower() in ('password', 'secret', 'token', 'api_key', 'apikey', 'authorization'):
                redacted[key] = '[REDACTED]'
            elif isinstance(value, str):
                redacted[key] = cls.redact(value)
            elif isinstance(value, dict):
                redacted[key] = cls.redact_dict(value)
            elif isinstance(value, list):
                redacted[key] = [
                    cls.redact(item) if isinstance(item, str)
                    else cls.redact_dict(item) if isinstance(item, dict)
                    else item
                    for item in value
                ]
            else:
                redacted[key] = value
        
        return redacted

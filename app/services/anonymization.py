"""
Anonymization service for sensitive data
"""
import hashlib
import re
from typing import Any, Dict
from cryptography.fernet import Fernet


class AnonymizationService:
    """Service to anonymize and encrypt sensitive data"""
    
    def __init__(self, encryption_key: bytes = None):
        """Initialize with encryption key"""
        if encryption_key is None:
            encryption_key = Fernet.generate_key()
        self.cipher = Fernet(encryption_key)
    
    def anonymize_email(self, email: str) -> str:
        """Anonymize email address"""
        if not email or '@' not in email:
            return "***@***"
        
        local, domain = email.split('@', 1)
        if len(local) <= 2:
            local_anon = '*' * len(local)
        else:
            local_anon = local[0] + '*' * (len(local) - 2) + local[-1]
        
        domain_parts = domain.split('.')
        if len(domain_parts) > 1:
            domain_anon = '*' * len(domain_parts[0]) + '.' + '.'.join(domain_parts[1:])
        else:
            domain_anon = '*' * len(domain)
        
        return f"{local_anon}@{domain_anon}"
    
    def anonymize_name(self, name: str) -> str:
        """Anonymize person name"""
        if not name:
            return "***"
        
        parts = name.split()
        if len(parts) == 0:
            return "***"
        elif len(parts) == 1:
            return parts[0][0] + '.' if len(parts[0]) > 0 else "***"
        else:
            # Keep first letter of first name, anonymize rest
            return parts[0][0] + '. ' + parts[-1][0] + '.'
    
    def anonymize_phone(self, phone: str) -> str:
        """Anonymize phone number"""
        # Remove all non-digits
        digits = re.sub(r'\D', '', phone)
        if len(digits) < 4:
            return "***-***-****"
        
        # Keep last 4 digits
        return f"***-***-{digits[-4:]}"
    
    def anonymize_ssn(self, ssn: str) -> str:
        """Anonymize SSN"""
        digits = re.sub(r'\D', '', ssn)
        if len(digits) < 4:
            return "***-**-****"
        
        return f"***-**-{digits[-4:]}"
    
    def anonymize_address(self, address: str) -> str:
        """Anonymize address"""
        if not address:
            return "***"
        
        # Keep city/state if identifiable, anonymize street
        parts = address.split(',')
        if len(parts) > 1:
            return "*** " + ','.join(parts[1:])
        return "***"
    
    def anonymize_field(self, field_name: str, value: str) -> str:
        """Anonymize a field based on its type"""
        field_name = field_name.lower()
        
        if 'email' in field_name:
            return self.anonymize_email(value)
        elif 'name' in field_name:
            return self.anonymize_name(value)
        elif 'phone' in field_name:
            return self.anonymize_phone(value)
        elif 'ssn' in field_name:
            return self.anonymize_ssn(value)
        elif 'address' in field_name:
            return self.anonymize_address(value)
        else:
            # Generic anonymization: hash
            return hashlib.sha256(value.encode()).hexdigest()[:16] + "..."
    
    def encrypt_data(self, data: str) -> str:
        """Encrypt sensitive data"""
        return self.cipher.encrypt(data.encode()).decode()
    
    def decrypt_data(self, encrypted_data: str) -> str:
        """Decrypt sensitive data"""
        return self.cipher.decrypt(encrypted_data.encode()).decode()
    
    def anonymize_dict(self, data: Dict[str, Any], sensitive_fields: list) -> Dict[str, Any]:
        """Anonymize multiple fields in a dictionary"""
        result = data.copy()
        for field in sensitive_fields:
            if field in result:
                result[field] = self.anonymize_field(field, str(result[field]))
        return result

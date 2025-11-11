"""Structured logging with PII redaction."""

import structlog
from typing import Any
from .config import config
from .pii_redactor import PIIRedactor


def configure_logging():
    """Configure structured logging with PII redaction."""
    processors = [
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
    ]
    
    # Add PII redaction processor if enabled
    if config.REDACT_PII:
        processors.append(redact_pii_processor)
    
    processors.append(structlog.dev.ConsoleRenderer())
    
    structlog.configure(
        processors=processors,
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )


def redact_pii_processor(logger: Any, method_name: str, event_dict: dict) -> dict:
    """Processor to redact PII from log events."""
    return PIIRedactor.redact_dict(event_dict)


def get_logger(name: str = "aurea"):
    """Get a configured logger instance."""
    return structlog.get_logger(name)


# Configure logging on module import
configure_logging()

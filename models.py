"""
Notification states for Aurea Orchestrator
"""
from enum import Enum


class NotificationState(str, Enum):
    """States that trigger notifications"""
    PLAN_READY = "PLAN_READY"
    NEEDS_REVISION = "NEEDS_REVISION"
    APPROVED = "APPROVED"
    FAILED = "FAILED"


class NotificationChannel(str, Enum):
    """Supported notification channels"""
    SLACK = "slack"
    EMAIL = "email"

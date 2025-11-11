"""
Configuration manager for notification settings
"""
import json
import os
from typing import Dict, List, Optional
from models import NotificationState, NotificationChannel


class NotificationConfig:
    """Manages notification configuration from JSON file"""
    
    def __init__(self, config_path: str = None):
        if config_path is None:
            config_path = os.getenv('NOTIFICATION_CONFIG_PATH', 'config/notifications.json')
        self.config_path = config_path
        self.config = self._load_config()
    
    def _load_config(self) -> Dict:
        """Load configuration from JSON file"""
        try:
            with open(self.config_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Warning: Config file {self.config_path} not found. Using empty config.")
            return {"organizations": []}
        except json.JSONDecodeError as e:
            print(f"Error parsing config file: {e}")
            return {"organizations": []}
    
    def get_org_config(self, org_id: str) -> Optional[Dict]:
        """Get configuration for a specific organization"""
        for org in self.config.get('organizations', []):
            if org.get('org_id') == org_id:
                return org
        return None
    
    def is_notification_enabled(self, org_id: str, state: NotificationState) -> bool:
        """Check if notifications are enabled for given org and state"""
        org_config = self.get_org_config(org_id)
        if not org_config or not org_config.get('notifications_enabled', False):
            return False
        
        state_rules = org_config.get('state_rules', {})
        state_config = state_rules.get(state.value, {})
        return state_config.get('enabled', False)
    
    def get_enabled_channels(self, org_id: str, state: NotificationState) -> List[str]:
        """Get list of enabled channels for given org and state"""
        org_config = self.get_org_config(org_id)
        if not org_config:
            return []
        
        state_rules = org_config.get('state_rules', {})
        state_config = state_rules.get(state.value, {})
        
        if not state_config.get('enabled', False):
            return []
        
        return state_config.get('channels', [])
    
    def get_slack_webhook(self, org_id: str) -> Optional[str]:
        """Get Slack webhook URL for organization"""
        org_config = self.get_org_config(org_id)
        if not org_config:
            return None
        
        slack_config = org_config.get('channels', {}).get('slack', {})
        if not slack_config.get('enabled', False):
            return None
        
        return slack_config.get('webhook_url')
    
    def get_email_recipients(self, org_id: str) -> List[str]:
        """Get email recipients for organization"""
        org_config = self.get_org_config(org_id)
        if not org_config:
            return []
        
        email_config = org_config.get('channels', {}).get('email', {})
        if not email_config.get('enabled', False):
            return []
        
        return email_config.get('recipients', [])
    
    def get_all_orgs(self) -> List[str]:
        """Get list of all organization IDs"""
        return [org.get('org_id') for org in self.config.get('organizations', [])]

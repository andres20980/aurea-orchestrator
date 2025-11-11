"""Configuration store for managing organization settings."""
import json
from typing import Dict, Optional
from pathlib import Path
from app.models.config import OrgConfig, RateLimitConfig


class ConfigStore:
    """In-memory configuration store with optional persistence."""
    
    def __init__(self, config_file: Optional[str] = None):
        self.config_file = config_file
        self._configs: Dict[str, OrgConfig] = {}
        self._load_config()
    
    def _load_config(self):
        """Load configuration from file if it exists."""
        if self.config_file and Path(self.config_file).exists():
            try:
                with open(self.config_file, 'r') as f:
                    data = json.load(f)
                    for org_id, config_data in data.items():
                        self._configs[org_id] = OrgConfig(**config_data)
            except Exception as e:
                print(f"Error loading config: {e}")
        
        # Set default config for 'default' org if not exists
        if 'default' not in self._configs:
            self._configs['default'] = OrgConfig(
                org_id='default',
                rate_limit=RateLimitConfig(),
                ip_allowlist=None,
                enabled=True
            )
    
    def _save_config(self):
        """Save configuration to file."""
        if self.config_file:
            try:
                with open(self.config_file, 'w') as f:
                    data = {
                        org_id: config.model_dump()
                        for org_id, config in self._configs.items()
                    }
                    json.dump(data, f, indent=2)
            except Exception as e:
                print(f"Error saving config: {e}")
    
    def get_org_config(self, org_id: str) -> OrgConfig:
        """Get configuration for an organization."""
        return self._configs.get(org_id, self._configs.get('default'))
    
    def update_rate_limit(self, org_id: str, requests_per_minute: Optional[int] = None,
                         requests_per_hour: Optional[int] = None) -> OrgConfig:
        """Update rate limit for an organization."""
        if org_id not in self._configs:
            self._configs[org_id] = OrgConfig(
                org_id=org_id,
                rate_limit=RateLimitConfig(),
                ip_allowlist=None,
                enabled=True
            )
        
        config = self._configs[org_id]
        if requests_per_minute is not None:
            config.rate_limit.requests_per_minute = requests_per_minute
        if requests_per_hour is not None:
            config.rate_limit.requests_per_hour = requests_per_hour
        
        self._save_config()
        return config
    
    def get_all_configs(self) -> Dict[str, OrgConfig]:
        """Get all organization configurations."""
        return self._configs.copy()
    
    def add_org_config(self, config: OrgConfig):
        """Add or update organization configuration."""
        self._configs[config.org_id] = config
        self._save_config()


# Global configuration store instance
config_store = ConfigStore()

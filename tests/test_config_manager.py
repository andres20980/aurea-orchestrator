"""
Unit tests for notification configuration manager
"""
import unittest
import json
import os
import tempfile
from models import NotificationState
from config_manager import NotificationConfig


class TestNotificationConfig(unittest.TestCase):
    """Test cases for NotificationConfig"""
    
    def setUp(self):
        """Set up test configuration file"""
        self.test_config = {
            "organizations": [
                {
                    "org_id": "test-org",
                    "org_name": "Test Organization",
                    "notifications_enabled": True,
                    "channels": {
                        "slack": {
                            "enabled": True,
                            "webhook_url": "https://hooks.slack.com/test",
                            "channel": "#test"
                        },
                        "email": {
                            "enabled": True,
                            "recipients": ["test@example.com"]
                        }
                    },
                    "state_rules": {
                        "PLAN_READY": {
                            "enabled": True,
                            "channels": ["slack", "email"]
                        },
                        "FAILED": {
                            "enabled": True,
                            "channels": ["slack"]
                        }
                    }
                }
            ]
        }
        
        # Create temporary config file
        self.temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json')
        json.dump(self.test_config, self.temp_file)
        self.temp_file.close()
        
        self.config = NotificationConfig(self.temp_file.name)
    
    def tearDown(self):
        """Clean up temporary file"""
        os.unlink(self.temp_file.name)
    
    def test_load_config(self):
        """Test configuration loading"""
        self.assertIsNotNone(self.config.config)
        self.assertEqual(len(self.config.config['organizations']), 1)
    
    def test_get_org_config(self):
        """Test getting organization configuration"""
        org_config = self.config.get_org_config('test-org')
        self.assertIsNotNone(org_config)
        self.assertEqual(org_config['org_name'], 'Test Organization')
        
        # Test non-existent org
        self.assertIsNone(self.config.get_org_config('non-existent'))
    
    def test_is_notification_enabled(self):
        """Test notification enabled check"""
        # Enabled state
        self.assertTrue(
            self.config.is_notification_enabled('test-org', NotificationState.PLAN_READY)
        )
        
        # Disabled state (not in config)
        self.assertFalse(
            self.config.is_notification_enabled('test-org', NotificationState.NEEDS_REVISION)
        )
        
        # Non-existent org
        self.assertFalse(
            self.config.is_notification_enabled('non-existent', NotificationState.PLAN_READY)
        )
    
    def test_get_enabled_channels(self):
        """Test getting enabled channels"""
        channels = self.config.get_enabled_channels('test-org', NotificationState.PLAN_READY)
        self.assertEqual(set(channels), {'slack', 'email'})
        
        channels = self.config.get_enabled_channels('test-org', NotificationState.FAILED)
        self.assertEqual(channels, ['slack'])
        
        # Disabled state
        channels = self.config.get_enabled_channels('test-org', NotificationState.NEEDS_REVISION)
        self.assertEqual(channels, [])
    
    def test_get_slack_webhook(self):
        """Test getting Slack webhook URL"""
        webhook = self.config.get_slack_webhook('test-org')
        self.assertEqual(webhook, 'https://hooks.slack.com/test')
        
        # Non-existent org
        self.assertIsNone(self.config.get_slack_webhook('non-existent'))
    
    def test_get_email_recipients(self):
        """Test getting email recipients"""
        recipients = self.config.get_email_recipients('test-org')
        self.assertEqual(recipients, ['test@example.com'])
        
        # Non-existent org
        self.assertEqual(self.config.get_email_recipients('non-existent'), [])
    
    def test_get_all_orgs(self):
        """Test getting all organization IDs"""
        orgs = self.config.get_all_orgs()
        self.assertEqual(orgs, ['test-org'])


if __name__ == '__main__':
    unittest.main()

"""
Main notification service that coordinates all notification channels
"""
from typing import Dict, List, Optional
from models import NotificationState, NotificationChannel
from config_manager import NotificationConfig
from slack_notifier import SlackNotifier
from email_notifier import EmailNotifier


class NotificationService:
    """
    Central notification service that manages all notification channels
    """
    
    def __init__(self, config_path: str = None):
        self.config = NotificationConfig(config_path)
        self.email_notifier = EmailNotifier()
    
    def send_notification(
        self,
        state: NotificationState,
        org_id: str,
        message: str,
        metadata: Optional[Dict] = None
    ) -> Dict[str, bool]:
        """
        Send notifications through all enabled channels for the given state and org
        
        Args:
            state: The notification state
            org_id: Organization identifier
            message: Main notification message
            metadata: Additional metadata to include
            
        Returns:
            Dictionary mapping channel names to success status
        """
        results = {}
        
        # Check if notifications are enabled for this org and state
        if not self.config.is_notification_enabled(org_id, state):
            print(f"Notifications disabled for org {org_id} and state {state.value}")
            return results
        
        # Get enabled channels for this state
        enabled_channels = self.config.get_enabled_channels(org_id, state)
        
        # Send Slack notification if enabled
        if NotificationChannel.SLACK.value in enabled_channels:
            webhook_url = self.config.get_slack_webhook(org_id)
            if webhook_url:
                slack_notifier = SlackNotifier(webhook_url)
                results['slack'] = slack_notifier.send_notification(
                    state, org_id, message, metadata
                )
            else:
                print(f"Slack enabled but no webhook URL configured for org {org_id}")
                results['slack'] = False
        
        # Send email notification if enabled
        if NotificationChannel.EMAIL.value in enabled_channels:
            recipients = self.config.get_email_recipients(org_id)
            if recipients:
                results['email'] = self.email_notifier.send_notification(
                    state, org_id, message, recipients, metadata
                )
            else:
                print(f"Email enabled but no recipients configured for org {org_id}")
                results['email'] = False
        
        return results
    
    def test_notification(self, org_id: str) -> Dict[str, any]:
        """
        Send test notifications through all configured channels for an organization
        
        Args:
            org_id: Organization identifier
            
        Returns:
            Dictionary with test results for each channel
        """
        results = {
            'org_id': org_id,
            'channels': {}
        }
        
        org_config = self.config.get_org_config(org_id)
        if not org_config:
            results['error'] = f"Organization {org_id} not found in configuration"
            return results
        
        test_message = "This is a test notification from Aurea Orchestrator"
        test_metadata = {
            "Test": "True",
            "Timestamp": __import__('datetime').datetime.now().isoformat()
        }
        
        # Test Slack
        slack_config = org_config.get('channels', {}).get('slack', {})
        if slack_config.get('enabled', False):
            webhook_url = slack_config.get('webhook_url')
            if webhook_url:
                slack_notifier = SlackNotifier(webhook_url)
                success = slack_notifier.send_notification(
                    NotificationState.PLAN_READY,
                    org_id,
                    test_message,
                    test_metadata
                )
                results['channels']['slack'] = {
                    'enabled': True,
                    'success': success,
                    'webhook_url': webhook_url[:50] + '...' if len(webhook_url) > 50 else webhook_url
                }
            else:
                results['channels']['slack'] = {
                    'enabled': True,
                    'success': False,
                    'error': 'No webhook URL configured'
                }
        else:
            results['channels']['slack'] = {'enabled': False}
        
        # Test Email
        email_config = org_config.get('channels', {}).get('email', {})
        if email_config.get('enabled', False):
            recipients = email_config.get('recipients', [])
            if recipients:
                success = self.email_notifier.send_notification(
                    NotificationState.PLAN_READY,
                    org_id,
                    test_message,
                    recipients,
                    test_metadata
                )
                results['channels']['email'] = {
                    'enabled': True,
                    'success': success,
                    'recipients': recipients
                }
            else:
                results['channels']['email'] = {
                    'enabled': True,
                    'success': False,
                    'error': 'No recipients configured'
                }
        else:
            results['channels']['email'] = {'enabled': False}
        
        return results

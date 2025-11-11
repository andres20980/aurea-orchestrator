"""
Unit tests for Slack notifier
"""
import unittest
from unittest.mock import patch, Mock
from models import NotificationState
from slack_notifier import SlackNotifier


class TestSlackNotifier(unittest.TestCase):
    """Test cases for SlackNotifier"""
    
    def setUp(self):
        """Set up test notifier"""
        self.webhook_url = "https://hooks.slack.com/services/TEST/WEBHOOK/URL"
        self.notifier = SlackNotifier(self.webhook_url)
    
    @patch('slack_notifier.requests.post')
    def test_send_notification_success(self, mock_post):
        """Test successful notification sending"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response
        
        result = self.notifier.send_notification(
            NotificationState.PLAN_READY,
            'test-org',
            'Test message'
        )
        
        self.assertTrue(result)
        self.assertTrue(mock_post.called)
        
        # Verify payload structure
        call_args = mock_post.call_args
        self.assertEqual(call_args[0][0], self.webhook_url)
        self.assertIn('headers', call_args[1])
        self.assertEqual(call_args[1]['headers']['Content-Type'], 'application/json')
    
    @patch('slack_notifier.requests.post')
    def test_send_notification_with_metadata(self, mock_post):
        """Test notification with metadata"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response
        
        metadata = {'key1': 'value1', 'key2': 'value2'}
        result = self.notifier.send_notification(
            NotificationState.FAILED,
            'test-org',
            'Test message',
            metadata
        )
        
        self.assertTrue(result)
    
    @patch('slack_notifier.requests.post')
    def test_send_notification_failure(self, mock_post):
        """Test failed notification sending"""
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.text = 'Bad request'
        mock_post.return_value = mock_response
        
        result = self.notifier.send_notification(
            NotificationState.PLAN_READY,
            'test-org',
            'Test message'
        )
        
        self.assertFalse(result)
    
    @patch('slack_notifier.requests.post')
    def test_send_notification_exception(self, mock_post):
        """Test notification sending with exception"""
        import requests
        mock_post.side_effect = requests.exceptions.RequestException('Network error')
        
        result = self.notifier.send_notification(
            NotificationState.PLAN_READY,
            'test-org',
            'Test message'
        )
        
        self.assertFalse(result)
    
    def test_build_payload_structure(self):
        """Test payload structure"""
        payload = self.notifier._build_payload(
            NotificationState.PLAN_READY,
            'test-org',
            'Test message',
            {'key': 'value'}
        )
        
        self.assertIn('attachments', payload)
        self.assertEqual(len(payload['attachments']), 1)
        
        attachment = payload['attachments'][0]
        self.assertIn('color', attachment)
        self.assertIn('title', attachment)
        self.assertIn('text', attachment)
        self.assertIn('fields', attachment)
        
        # Check fields
        field_titles = [f['title'] for f in attachment['fields']]
        self.assertIn('Organization', field_titles)
        self.assertIn('State', field_titles)
        self.assertIn('key', field_titles)
    
    def test_no_webhook_url(self):
        """Test with no webhook URL"""
        notifier = SlackNotifier(None)
        result = notifier.send_notification(
            NotificationState.PLAN_READY,
            'test-org',
            'Test message'
        )
        self.assertFalse(result)


if __name__ == '__main__':
    unittest.main()

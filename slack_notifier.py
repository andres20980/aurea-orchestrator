"""
Slack notification handler
"""
import requests
import json
from typing import Dict, Optional
from models import NotificationState


class SlackNotifier:
    """Handles Slack webhook notifications"""
    
    def __init__(self, webhook_url: str):
        self.webhook_url = webhook_url
    
    def send_notification(
        self, 
        state: NotificationState, 
        org_id: str,
        message: str,
        metadata: Optional[Dict] = None
    ) -> bool:
        """
        Send notification to Slack
        
        Args:
            state: The notification state
            org_id: Organization identifier
            message: Main notification message
            metadata: Additional metadata to include
            
        Returns:
            True if notification was sent successfully, False otherwise
        """
        if not self.webhook_url:
            print("No Slack webhook URL configured")
            return False
        
        # Build Slack message payload
        payload = self._build_payload(state, org_id, message, metadata)
        
        try:
            response = requests.post(
                self.webhook_url,
                data=json.dumps(payload),
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            if response.status_code == 200:
                print(f"Slack notification sent successfully for {state.value}")
                return True
            else:
                print(f"Failed to send Slack notification: {response.status_code} - {response.text}")
                return False
                
        except requests.exceptions.RequestException as e:
            print(f"Error sending Slack notification: {e}")
            return False
    
    def _build_payload(
        self, 
        state: NotificationState, 
        org_id: str,
        message: str,
        metadata: Optional[Dict] = None
    ) -> Dict:
        """Build Slack message payload with formatting"""
        
        # Color coding for different states
        color_map = {
            NotificationState.PLAN_READY: "#36a64f",  # Green
            NotificationState.NEEDS_REVISION: "#ff9900",  # Orange
            NotificationState.APPROVED: "#2eb886",  # Teal
            NotificationState.FAILED: "#ff0000"  # Red
        }
        
        # Emoji for different states
        emoji_map = {
            NotificationState.PLAN_READY: ":white_check_mark:",
            NotificationState.NEEDS_REVISION: ":warning:",
            NotificationState.APPROVED: ":tada:",
            NotificationState.FAILED: ":x:"
        }
        
        color = color_map.get(state, "#808080")
        emoji = emoji_map.get(state, ":information_source:")
        
        # Build attachments
        attachment = {
            "color": color,
            "title": f"{emoji} {state.value}",
            "text": message,
            "fields": [
                {
                    "title": "Organization",
                    "value": org_id,
                    "short": True
                },
                {
                    "title": "State",
                    "value": state.value,
                    "short": True
                }
            ],
            "footer": "Aurea Orchestrator",
            "ts": int(__import__('time').time())
        }
        
        # Add metadata fields if provided
        if metadata:
            for key, value in metadata.items():
                attachment["fields"].append({
                    "title": key,
                    "value": str(value),
                    "short": True
                })
        
        return {
            "attachments": [attachment]
        }

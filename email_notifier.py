"""
Email notification handler
"""
import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Dict, Optional
from models import NotificationState


class EmailNotifier:
    """Handles email notifications"""
    
    def __init__(
        self,
        smtp_host: str = None,
        smtp_port: int = None,
        smtp_username: str = None,
        smtp_password: str = None,
        from_email: str = None,
        use_tls: bool = True
    ):
        self.smtp_host = smtp_host or os.getenv('SMTP_HOST', 'smtp.gmail.com')
        self.smtp_port = smtp_port or int(os.getenv('SMTP_PORT', '587'))
        self.smtp_username = smtp_username or os.getenv('SMTP_USERNAME', '')
        self.smtp_password = smtp_password or os.getenv('SMTP_PASSWORD', '')
        self.from_email = from_email or os.getenv('SMTP_FROM_EMAIL', 'noreply@aurea-orchestrator.com')
        self.use_tls = use_tls if use_tls is not None else os.getenv('SMTP_USE_TLS', 'true').lower() == 'true'
    
    def send_notification(
        self,
        state: NotificationState,
        org_id: str,
        message: str,
        recipients: List[str],
        metadata: Optional[Dict] = None
    ) -> bool:
        """
        Send email notification
        
        Args:
            state: The notification state
            org_id: Organization identifier
            message: Main notification message
            recipients: List of email recipients
            metadata: Additional metadata to include
            
        Returns:
            True if notification was sent successfully, False otherwise
        """
        if not recipients:
            print("No email recipients configured")
            return False
        
        if not self.smtp_username or not self.smtp_password:
            print("SMTP credentials not configured")
            return False
        
        subject = self._get_subject(state, org_id)
        html_body = self._build_html_body(state, org_id, message, metadata)
        
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.from_email
            msg['To'] = ', '.join(recipients)
            
            # Attach HTML body
            html_part = MIMEText(html_body, 'html')
            msg.attach(html_part)
            
            # Send email
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                if self.use_tls:
                    server.starttls()
                server.login(self.smtp_username, self.smtp_password)
                server.send_message(msg)
            
            print(f"Email notification sent successfully for {state.value} to {len(recipients)} recipients")
            return True
            
        except Exception as e:
            print(f"Error sending email notification: {e}")
            return False
    
    def _get_subject(self, state: NotificationState, org_id: str) -> str:
        """Generate email subject line"""
        return f"[Aurea Orchestrator] {state.value} - {org_id}"
    
    def _build_html_body(
        self,
        state: NotificationState,
        org_id: str,
        message: str,
        metadata: Optional[Dict] = None
    ) -> str:
        """Build HTML email body"""
        
        # Color coding for different states
        color_map = {
            NotificationState.PLAN_READY: "#36a64f",
            NotificationState.NEEDS_REVISION: "#ff9900",
            NotificationState.APPROVED: "#2eb886",
            NotificationState.FAILED: "#ff0000"
        }
        
        color = color_map.get(state, "#808080")
        
        metadata_html = ""
        if metadata:
            metadata_rows = ""
            for key, value in metadata.items():
                metadata_rows += f"""
                <tr>
                    <td style="padding: 8px; border: 1px solid #ddd;"><strong>{key}</strong></td>
                    <td style="padding: 8px; border: 1px solid #ddd;">{value}</td>
                </tr>
                """
            metadata_html = f"""
            <h3>Additional Details</h3>
            <table style="border-collapse: collapse; width: 100%;">
                {metadata_rows}
            </table>
            """
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
        </head>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <div style="background-color: {color}; color: white; padding: 20px; border-radius: 5px 5px 0 0;">
                    <h1 style="margin: 0;">{state.value}</h1>
                </div>
                <div style="background-color: #f9f9f9; padding: 20px; border: 1px solid #ddd; border-top: none; border-radius: 0 0 5px 5px;">
                    <h2>Organization: {org_id}</h2>
                    <p>{message}</p>
                    {metadata_html}
                    <hr style="margin: 20px 0; border: none; border-top: 1px solid #ddd;">
                    <p style="color: #666; font-size: 12px;">
                        This is an automated notification from Aurea Orchestrator.
                    </p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return html

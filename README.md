# Aurea Orchestrator
Automated Unified Reasoning & Execution Agents

## Notification Layer

The Aurea Orchestrator includes a comprehensive notification system that supports Slack webhooks and email notifications for key workflow states.

### Features

- **Multi-channel notifications**: Slack and Email
- **State-based triggers**: PLAN_READY, NEEDS_REVISION, APPROVED, FAILED
- **Per-organization configuration**: Custom channels and opt-in rules for each organization
- **Test endpoint**: Validate notification configuration with `/notifications/test`

### Quick Start

1. **Install dependencies**:
```bash
pip install -r requirements.txt
```

2. **Configure environment variables**:
```bash
cp .env.example .env
# Edit .env with your SMTP settings
```

3. **Configure organizations**:
Edit `config/notifications.json` to set up your organizations, channels, and notification rules.

4. **Run the service**:
```bash
python app.py
```

The service will start on port 5000 by default.

### API Endpoints

#### Send Notification
```http
POST /notifications/send
Content-Type: application/json

{
  "state": "PLAN_READY",
  "org_id": "default",
  "message": "Plan is ready for review",
  "metadata": {
    "plan_id": "12345",
    "author": "john.doe"
  }
}
```

#### Test Notifications
```http
POST /notifications/test
Content-Type: application/json

{
  "org_id": "default"
}
```

This will send test notifications through all configured channels for the specified organization.

#### Get Configuration
```http
GET /notifications/config?org_id=default
```

#### Get Valid States
```http
GET /notifications/states
```

#### Health Check
```http
GET /health
```

### Configuration

#### Environment Variables (Secrets)

The following environment variables should be configured in your `.env` file or deployment environment:

**Email Configuration** (Required for email notifications):
- `SMTP_HOST`: SMTP server hostname (e.g., `smtp.gmail.com`)
- `SMTP_PORT`: SMTP server port (e.g., `587` for TLS)
- `SMTP_USERNAME`: SMTP authentication username
- `SMTP_PASSWORD`: SMTP authentication password (use app-specific password for Gmail)
- `SMTP_FROM_EMAIL`: Sender email address
- `SMTP_USE_TLS`: Enable TLS encryption (`true` or `false`)

**Application Configuration**:
- `FLASK_ENV`: Environment mode (`development` or `production`)
- `PORT`: Server port (default: `5000`)
- `NOTIFICATION_CONFIG_PATH`: Path to notification config file (default: `config/notifications.json`)

#### Organization Configuration

Edit `config/notifications.json` to configure per-organization notification settings:

```json
{
  "organizations": [
    {
      "org_id": "your-org-id",
      "org_name": "Your Organization",
      "notifications_enabled": true,
      "channels": {
        "slack": {
          "enabled": true,
          "webhook_url": "https://hooks.slack.com/services/YOUR/WEBHOOK/URL",
          "channel": "#notifications"
        },
        "email": {
          "enabled": true,
          "recipients": ["team@example.com", "alerts@example.com"]
        }
      },
      "state_rules": {
        "PLAN_READY": {
          "enabled": true,
          "channels": ["slack", "email"]
        },
        "NEEDS_REVISION": {
          "enabled": true,
          "channels": ["slack", "email"]
        },
        "APPROVED": {
          "enabled": true,
          "channels": ["slack"]
        },
        "FAILED": {
          "enabled": true,
          "channels": ["slack", "email"]
        }
      }
    }
  ]
}
```

### Notification States

The system supports four notification states:

1. **PLAN_READY**: Triggered when a plan is ready for review
2. **NEEDS_REVISION**: Triggered when a plan requires changes
3. **APPROVED**: Triggered when a plan is approved
4. **FAILED**: Triggered when a workflow fails

### Opt-in Rules

Notifications are opt-in at multiple levels:

1. **Organization level**: Set `notifications_enabled: true` for the organization
2. **Channel level**: Enable specific channels in the `channels` configuration
3. **State level**: Enable notifications for specific states in `state_rules`
4. **Per-state channel selection**: Choose which channels receive notifications for each state

This allows fine-grained control over when and how notifications are sent.

### Security Best Practices

- **Never commit secrets**: Use environment variables for sensitive data (SMTP credentials, Slack webhooks)
- **Use app-specific passwords**: For Gmail, generate an app-specific password rather than using your main password
- **Restrict webhook URLs**: Keep Slack webhook URLs secure and rotate them if compromised
- **Validate configuration**: Use the `/notifications/test` endpoint to verify setup before going live

### Example Usage

Send a notification when a plan is ready:
```bash
curl -X POST http://localhost:5000/notifications/send \
  -H "Content-Type: application/json" \
  -d '{
    "state": "PLAN_READY",
    "org_id": "default",
    "message": "Deployment plan #42 is ready for review",
    "metadata": {
      "plan_id": "42",
      "environment": "production",
      "author": "jane.doe"
    }
  }'
```

Test notification configuration:
```bash
curl -X POST http://localhost:5000/notifications/test \
  -H "Content-Type: application/json" \
  -d '{"org_id": "default"}'
```

### Development

The service is built with:
- **Flask**: Web framework
- **Requests**: HTTP client for Slack webhooks
- **Python SMTP**: Email delivery
- **Pydantic**: Data validation and settings management

### License

MIT

"""
Flask REST API for Aurea Orchestrator Notification Service
"""
from flask import Flask, request, jsonify
from dotenv import load_dotenv
import os

from notification_service import NotificationService
from models import NotificationState

# Load environment variables
load_dotenv()

app = Flask(__name__)
notification_service = NotificationService()


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'aurea-orchestrator-notifications'
    }), 200


@app.route('/notifications/send', methods=['POST'])
def send_notification():
    """
    Send a notification
    
    Request body:
    {
        "state": "PLAN_READY|NEEDS_REVISION|APPROVED|FAILED",
        "org_id": "organization-id",
        "message": "Notification message",
        "metadata": {  // optional
            "key": "value"
        }
    }
    """
    try:
        data = request.get_json(force=True, silent=True)
        
        # Validate required fields
        if not data:
            return jsonify({'error': 'Request body is required'}), 400
        
        state_str = data.get('state')
        org_id = data.get('org_id')
        message = data.get('message')
        
        if not state_str:
            return jsonify({'error': 'state is required'}), 400
        if not org_id:
            return jsonify({'error': 'org_id is required'}), 400
        if not message:
            return jsonify({'error': 'message is required'}), 400
        
        # Validate state
        try:
            state = NotificationState(state_str)
        except ValueError:
            valid_states = [s.value for s in NotificationState]
            return jsonify({
                'error': f'Invalid state. Must be one of: {", ".join(valid_states)}'
            }), 400
        
        # Get optional metadata
        metadata = data.get('metadata', {})
        
        # Send notification
        results = notification_service.send_notification(
            state, org_id, message, metadata
        )
        
        return jsonify({
            'status': 'success',
            'org_id': org_id,
            'state': state.value,
            'channels_sent': results
        }), 200
        
    except Exception as e:
        return jsonify({
            'error': 'Internal server error',
            'details': str(e)
        }), 500


@app.route('/notifications/test', methods=['POST'])
def test_notification():
    """
    Test notification configuration for an organization
    
    Request body:
    {
        "org_id": "organization-id"
    }
    """
    try:
        data = request.get_json(force=True, silent=True)
        
        if not data:
            return jsonify({'error': 'Request body is required'}), 400
        
        org_id = data.get('org_id')
        if not org_id:
            return jsonify({'error': 'org_id is required'}), 400
        
        # Run test
        results = notification_service.test_notification(org_id)
        
        if 'error' in results:
            return jsonify(results), 404
        
        return jsonify({
            'status': 'test_complete',
            **results
        }), 200
        
    except Exception as e:
        return jsonify({
            'error': 'Internal server error',
            'details': str(e)
        }), 500


@app.route('/notifications/config', methods=['GET'])
def get_config():
    """
    Get notification configuration
    
    Query params:
    - org_id: (optional) Get config for specific organization
    """
    try:
        org_id = request.args.get('org_id')
        
        if org_id:
            org_config = notification_service.config.get_org_config(org_id)
            if not org_config:
                return jsonify({'error': f'Organization {org_id} not found'}), 404
            
            # Sanitize sensitive data
            sanitized_config = org_config.copy()
            if 'channels' in sanitized_config:
                if 'slack' in sanitized_config['channels']:
                    webhook = sanitized_config['channels']['slack'].get('webhook_url', '')
                    if webhook:
                        sanitized_config['channels']['slack']['webhook_url'] = webhook[:50] + '...'
            
            return jsonify(sanitized_config), 200
        else:
            # Return list of all orgs
            orgs = notification_service.config.get_all_orgs()
            return jsonify({
                'organizations': orgs
            }), 200
            
    except Exception as e:
        return jsonify({
            'error': 'Internal server error',
            'details': str(e)
        }), 500


@app.route('/notifications/states', methods=['GET'])
def get_states():
    """Get list of valid notification states"""
    return jsonify({
        'states': [state.value for state in NotificationState]
    }), 200


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_ENV') == 'development'
    app.run(host='0.0.0.0', port=port, debug=debug)

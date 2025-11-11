"""
Unit tests for Flask API
"""
import unittest
import json
from app import app


class TestAPI(unittest.TestCase):
    """Test cases for Flask API endpoints"""
    
    def setUp(self):
        """Set up test client"""
        self.app = app
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()
    
    def test_health_check(self):
        """Test health check endpoint"""
        response = self.client.get('/health')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'healthy')
        self.assertIn('service', data)
    
    def test_get_states(self):
        """Test get states endpoint"""
        response = self.client.get('/notifications/states')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertIn('states', data)
        self.assertIn('PLAN_READY', data['states'])
        self.assertIn('NEEDS_REVISION', data['states'])
        self.assertIn('APPROVED', data['states'])
        self.assertIn('FAILED', data['states'])
    
    def test_send_notification_missing_body(self):
        """Test send notification with missing body"""
        response = self.client.post('/notifications/send')
        self.assertEqual(response.status_code, 400)
        
        data = json.loads(response.data)
        self.assertIn('error', data)
    
    def test_send_notification_missing_fields(self):
        """Test send notification with missing required fields"""
        response = self.client.post(
            '/notifications/send',
            data=json.dumps({'state': 'PLAN_READY'}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
        
        data = json.loads(response.data)
        self.assertIn('error', data)
    
    def test_send_notification_invalid_state(self):
        """Test send notification with invalid state"""
        response = self.client.post(
            '/notifications/send',
            data=json.dumps({
                'state': 'INVALID_STATE',
                'org_id': 'test-org',
                'message': 'Test message'
            }),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
        
        data = json.loads(response.data)
        self.assertIn('error', data)
    
    def test_test_notification_missing_body(self):
        """Test test notification with missing body"""
        response = self.client.post('/notifications/test')
        self.assertEqual(response.status_code, 400)
        
        data = json.loads(response.data)
        self.assertIn('error', data)
    
    def test_test_notification_missing_org_id(self):
        """Test test notification with missing org_id"""
        response = self.client.post(
            '/notifications/test',
            data=json.dumps({}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
        
        data = json.loads(response.data)
        self.assertIn('error', data)
    
    def test_get_config_all_orgs(self):
        """Test get all organizations"""
        response = self.client.get('/notifications/config')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertIn('organizations', data)
    
    def test_get_config_specific_org(self):
        """Test get specific org config"""
        response = self.client.get('/notifications/config?org_id=default')
        # Should return 200 if org exists, 404 if not
        self.assertIn(response.status_code, [200, 404])


if __name__ == '__main__':
    unittest.main()

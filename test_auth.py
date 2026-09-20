"""
Authentication Module Automated Test Script
"""
import sys
import unittest
import json
import os
from pathlib import Path

# Add project root directory to path
sys.path.append(str(Path(__file__).resolve().parent))

from backend.app import create_app
from database.models import User
from config.settings import Config

class TestConfig(Config):
    TESTING = True
    DB_PATH = Path(__file__).resolve().parent / 'database' / 'test_waste.db'

class AuthTestCase(unittest.TestCase):
    def setUp(self):
        """Configure fresh test database for each isolated test."""
        self.test_db_path = TestConfig.DB_PATH
        
        if os.path.exists(self.test_db_path):
            try:
                os.remove(self.test_db_path)
            except Exception:
                pass

        self.app = create_app(config_class=TestConfig)
        self.client = self.app.test_client()

    def tearDown(self):
        """Remove test database after test run."""
        if os.path.exists(self.test_db_path):
            try:
                os.remove(self.test_db_path)
            except Exception:
                pass

    def test_user_registration_and_password_hashing(self):
        """Test user registration and verify password is stored as hash, not plaintext."""
        response = self.client.post('/api/auth/register', json={
            'username': 'pradnya_mote',
            'email': 'pradnya@example.com',
            'password': 'securepassword123',
            'role': 'admin'
        })
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 201)
        self.assertTrue(data['success'])
        self.assertEqual(data['user']['username'], 'pradnya_mote')

        # Verify password is NOT stored as raw text in DB
        with self.app.app_context():
            user = User.get_by_username('pradnya_mote')
            self.assertIsNotNone(user)
            self.assertNotEqual(user.password_hash, 'securepassword123')
            self.assertTrue(user.check_password('securepassword123'))
            self.assertFalse(user.check_password('wrongpassword'))

    def test_duplicate_user_registration(self):
        """Test error handling when registering duplicate username or email."""
        self.client.post('/api/auth/register', json={
            'username': 'admin_user',
            'email': 'admin@example.com',
            'password': 'adminpassword'
        })

        # Attempt registering same username
        response = self.client.post('/api/auth/register', json={
            'username': 'admin_user',
            'email': 'different@example.com',
            'password': 'password123'
        })
        self.assertEqual(response.status_code, 409)

    def test_login_logout_session_flow(self):
        """Test complete workflow: registration -> login -> check session -> logout."""
        # 1. Register User
        self.client.post('/api/auth/register', json={
            'username': 'sanitation_driver',
            'email': 'driver@waste.gov',
            'password': 'driverpassword123',
            'role': 'driver'
        })

        # 2. Login with valid credentials
        login_res = self.client.post('/api/auth/login', json={
            'username_or_email': 'driver@waste.gov',
            'password': 'driverpassword123'
        })
        self.assertEqual(login_res.status_code, 200)

        # 3. Verify session endpoint (/api/auth/me)
        me_res = self.client.get('/api/auth/me')
        me_data = json.loads(me_res.data)
        self.assertEqual(me_res.status_code, 200)
        self.assertTrue(me_data['authenticated'])
        self.assertEqual(me_data['user']['role'], 'driver')

        # 4. Logout
        logout_res = self.client.post('/api/auth/logout')
        self.assertEqual(logout_res.status_code, 200)

        # 5. Verify session is cleared
        me_res_after_logout = self.client.get('/api/auth/me')
        self.assertEqual(me_res_after_logout.status_code, 401)

if __name__ == '__main__':
    print("Running Authentication Backend Unit Tests...\n")
    unittest.main()

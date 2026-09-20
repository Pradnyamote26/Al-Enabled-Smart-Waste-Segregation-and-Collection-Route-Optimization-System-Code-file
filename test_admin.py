"""
Admin Subsystem & Access Control Automated Unit Test Suite
"""
import sys
import unittest
import json
import os
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent))

from backend.app import create_app
from database.models import User, WasteCategory, WasteDetection, Location, Route
from config.settings import Config

class TestConfig(Config):
    TESTING = True
    DB_PATH = Path(__file__).resolve().parent / 'database' / 'test_admin.db'

class AdminTestCase(unittest.TestCase):
    def setUp(self):
        """Configure clean test environment with admin & normal users."""
        self.test_db_path = TestConfig.DB_PATH
        if os.path.exists(self.test_db_path):
            try:
                os.remove(self.test_db_path)
            except Exception:
                pass

        self.app = create_app(config_class=TestConfig)
        self.client = self.app.test_client()

        # Create test users
        with self.app.app_context():
            User.create('admin_test', 'admin@test.gov', 'adminpass123', role='admin')
            User.create('user_test', 'user@test.gov', 'userpass123', role='user')

    def tearDown(self):
        """Clean up test database."""
        if os.path.exists(self.test_db_path):
            try:
                os.remove(self.test_db_path)
            except Exception:
                pass

    def test_unauthorized_access_restriction(self):
        """Verify non-admin requests are rejected with 403 Forbidden."""
        # Attempt accessing admin endpoint without login
        res = self.client.get('/api/admin/users')
        self.assertEqual(res.status_code, 403)

        # Login as normal user
        self.client.post('/api/auth/login', json={'username_or_email': 'user_test', 'password': 'userpass123'})
        res = self.client.get('/api/admin/users')
        self.assertEqual(res.status_code, 403)

    def test_admin_authorized_crud_operations(self):
        """Verify admin can view, create, and delete records."""
        # 1. Login as Admin
        login_res = self.client.post('/api/auth/login', json={'username_or_email': 'admin_test', 'password': 'adminpass123'})
        self.assertEqual(login_res.status_code, 200)

        # 2. View Admin Stats
        stats_res = self.client.get('/api/admin/stats')
        self.assertEqual(stats_res.status_code, 200)

        # 3. View Users List
        users_res = self.client.get('/api/admin/users')
        self.assertEqual(users_res.status_code, 200)
        users_data = json.loads(users_res.data)
        self.assertGreaterEqual(len(users_data['users']), 2)

        # 4. Create & Delete Master Category
        cat_res = self.client.post('/api/admin/categories', json={
            'category_name': 'E-Waste Electronics',
            'waste_type': 'Hazardous Waste',
            'recommended_bin_color': 'Black',
            'disposal_suggestion': 'Dispose at specialized municipal e-waste drop-off center.'
        })
        self.assertEqual(cat_res.status_code, 201)
        cat_data = json.loads(cat_res.data)
        cat_id = cat_data['category']['id']

        del_res = self.client.delete(f'/api/admin/categories/{cat_id}')
        self.assertEqual(del_res.status_code, 200)

if __name__ == '__main__':
    print("Running Admin Portal Backend Unit Tests...\n")
    unittest.main()

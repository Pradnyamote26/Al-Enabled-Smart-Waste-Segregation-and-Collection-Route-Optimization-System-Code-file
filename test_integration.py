"""
Complete End-to-End System Integration Test Suite
"""
import sys
import unittest
import json
import io
import os
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent))

from backend.app import create_app
from database.models import User, WasteDetection, Location, Route
from config.settings import Config

class TestConfig(Config):
    TESTING = True
    DB_PATH = Path(__file__).resolve().parent / 'database' / 'test_integration.db'

class IntegrationTestCase(unittest.TestCase):
    def setUp(self):
        """Configure test database environment."""
        self.test_db_path = TestConfig.DB_PATH
        if os.path.exists(self.test_db_path):
            try:
                os.remove(self.test_db_path)
            except Exception:
                pass

        self.app = create_app(config_class=TestConfig)
        self.client = self.app.test_client()

    def tearDown(self):
        """Clean up test database."""
        if os.path.exists(self.test_db_path):
            try:
                os.remove(self.test_db_path)
            except Exception:
                pass

    def _create_sample_image_bytes(self):
        ppm_header = b'P6\n1 1\n255\n'
        pixel_data = b'\x00\xff\x00'
        return io.BytesIO(ppm_header + pixel_data)

    def test_full_application_workflow_integration(self):
        """
        Executes complete end-to-end user workflow:
        User Login -> Upload Image -> AI Classification -> Save DB -> Add Location -> Route Optimization -> Save Route -> Dashboard Metrics -> Admin Control
        """

        # Step 1: User Registration & Login
        reg_res = self.client.post('/api/auth/register', json={
            'username': 'integration_user',
            'email': 'user@integration.com',
            'password': 'password123',
            'role': 'user'
        })
        self.assertEqual(reg_res.status_code, 201)

        login_res = self.client.post('/api/auth/login', json={
            'username_or_email': 'integration_user',
            'password': 'password123'
        })
        self.assertEqual(login_res.status_code, 200)

        # Step 2: Upload Waste Image & AI Classification
        img_bytes = self._create_sample_image_bytes()
        classify_res = self.client.post('/api/classify', data={
            'image': (img_bytes, 'waste_plastic_bottle.jpg')
        }, content_type='multipart/form-data')

        classify_data = json.loads(classify_res.data)
        self.assertEqual(classify_res.status_code, 200)
        self.assertTrue(classify_data['success'])
        self.assertIn('category_name', classify_data)
        self.assertIn('waste_type', classify_data)
        self.assertIn('disposal_suggestion', classify_data)

        # Step 3: Verify Result Stored in Database
        with self.app.app_context():
            detections = WasteDetection.get_recent(limit=5)
            self.assertGreaterEqual(len(detections), 1)
            self.assertEqual(detections[0].category_name, classify_data['category_name'])

        # Step 4: Add Collection Location Point
        loc_res = self.client.post('/api/locations', json={
            'location_name': 'Bin #10 - Sector 5 Community Center',
            'latitude': 18.5250,
            'longitude': 73.8610,
            'current_fill_level': 85.0,
            'current_weight_kg': 110.0,
            'priority': 5
        })
        self.assertEqual(loc_res.status_code, 201)

        # Step 5: Generate & Store Optimized Route Plan
        route_res = self.client.post('/api/optimize_route', json={
            'depot_lat': 18.5204,
            'depot_lng': 73.8567,
            'depot_name': 'Central Municipal Depot'
        })
        route_data = json.loads(route_res.data)
        self.assertEqual(route_res.status_code, 200)
        self.assertTrue(route_data['success'])
        self.assertGreater(route_data['total_distance_km'], 0)

        # Step 6: Query Dashboard Metrics
        dash_res = self.client.get('/api/dashboard/stats')
        dash_data = json.loads(dash_res.data)
        self.assertEqual(dash_res.status_code, 200)
        self.assertEqual(dash_data['summary']['total_detections'], 1)
        self.assertGreaterEqual(dash_data['summary']['total_bins'], 1)

        # Step 7: Admin Verification
        with self.app.app_context():
            User.create('admin_integration', 'admin@integration.com', 'admin123', role='admin')

        self.client.post('/api/auth/login', json={
            'username_or_email': 'admin_integration',
            'password': 'admin123'
        })

        admin_stats_res = self.client.get('/api/admin/stats')
        admin_data = json.loads(admin_stats_res.data)
        self.assertEqual(admin_stats_res.status_code, 200)
        self.assertTrue(admin_data['success'])

if __name__ == '__main__':
    print("Running Full End-to-End System Integration Test Suite...\n")
    unittest.main()

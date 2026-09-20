"""
Dashboard Analytics API Unit Test Suite
"""
import sys
import unittest
import json
import os
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent))

from backend.app import create_app
from config.settings import Config

class TestConfig(Config):
    TESTING = True
    DB_PATH = Path(__file__).resolve().parent / 'database' / 'test_dashboard.db'

class DashboardTestCase(unittest.TestCase):
    def setUp(self):
        """Configure test environment."""
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

    def test_dashboard_stats_api(self):
        """Test dashboard stats endpoint payload structure."""
        res = self.client.get('/api/dashboard/stats')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertIn('summary', data)
        self.assertIn('chart_category', data)
        self.assertIn('chart_bin_status', data)
        self.assertIn('recent_detections', data)
        self.assertIn('urgent_bins', data)
        self.assertIn('total_detections', data['summary'])
        self.assertIn('total_bins', data['summary'])

if __name__ == '__main__':
    print("Running Dashboard Backend Unit Tests...\n")
    unittest.main()

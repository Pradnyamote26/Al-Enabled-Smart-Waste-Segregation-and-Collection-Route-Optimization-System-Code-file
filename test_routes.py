"""
Route Optimization Module Automated Unit Test Suite
"""
import sys
import unittest
import json
import os
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent))

from backend.app import create_app
from database.models import Location, Route
from config.settings import Config

class TestConfig(Config):
    TESTING = True
    DB_PATH = Path(__file__).resolve().parent / 'database' / 'test_routes.db'

class RouteTestCase(unittest.TestCase):
    def setUp(self):
        """Configure clean test environment."""
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

    def test_locations_crud(self):
        """Test fetching, adding, and deleting collection points."""
        # 1. Fetch default seeded locations
        res = self.client.get('/api/locations')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        initial_count = data['count']

        # 2. Add new location
        add_res = self.client.post('/api/locations', json={
            'location_name': 'Test Bin #99 - Innovation Lab',
            'latitude': 18.5220,
            'longitude': 73.8580,
            'current_fill_level': 88.0,
            'current_weight_kg': 95.0,
            'priority': 4
        })
        add_data = json.loads(add_res.data)
        self.assertEqual(add_res.status_code, 201)
        self.assertTrue(add_data['success'])
        new_id = add_data['location']['id']

        # 3. Verify count increased
        res_after = self.client.get('/api/locations')
        data_after = json.loads(res_after.data)
        self.assertEqual(data_after['count'], initial_count + 1)

        # 4. Delete location
        del_res = self.client.delete(f'/api/locations/{new_id}')
        self.assertEqual(del_res.status_code, 200)

    def test_route_optimization_algorithm_execution(self):
        """Test route optimization computation, distance, time, and DB logging."""
        response = self.client.post('/api/optimize_route', json={
            'depot_lat': 18.5204,
            'depot_lng': 73.8567,
            'depot_name': 'Central Campus Depot'
        })
        data = json.loads(response.data)

        # Assert response structure
        self.assertEqual(response.status_code, 200)
        self.assertTrue(data['success'])
        self.assertIn('total_distance_km', data)
        self.assertIn('estimated_time_mins', data)
        self.assertIn('fuel_used_liters', data)
        self.assertIn('stops', data)
        self.assertGreater(len(data['stops']), 2)  # Depot start, bins, depot finish

        # Verify Database route log persistence
        with self.app.app_context():
            routes = Route.get_recent(limit=5)
            self.assertGreaterEqual(len(routes), 1)
            latest = routes[0]
            self.assertEqual(latest.total_distance_km, data['total_distance_km'])
            self.assertEqual(latest.estimated_time_mins, data['estimated_time_mins'])

if __name__ == '__main__':
    print("Running Route Optimization Backend Unit Tests...\n")
    unittest.main()

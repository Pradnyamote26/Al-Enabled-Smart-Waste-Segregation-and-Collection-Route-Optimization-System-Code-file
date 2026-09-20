"""
AI Waste Classification Engine Automated Unit Test Suite
"""
import sys
import unittest
import json
import io
import os
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent))

from backend.app import create_app
from database.models import WasteDetection
from config.settings import Config

class TestConfig(Config):
    TESTING = True
    DB_PATH = Path(__file__).resolve().parent / 'database' / 'test_classification.db'

class ClassificationTestCase(unittest.TestCase):
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

    def _create_sample_image_bytes(self):
        """Creates an in-memory sample 1x1 PPM image for testing without PIL."""
        ppm_header = b'P6\n1 1\n255\n'
        pixel_data = b'\x00\xff\x00'  # Green pixel
        return io.BytesIO(ppm_header + pixel_data)

    def test_image_classification_api_and_db_storage(self):
        """Test uploading a waste image, classification API execution, and DB record persistence."""
        image_bytes = self._create_sample_image_bytes()

        response = self.client.post('/api/classify', data={
            'image': (image_bytes, 'plastic_bottle.jpg')
        }, content_type='multipart/form-data')

        data = json.loads(response.data)

        # 1. Assert HTTP Status & JSON Response structure
        self.assertEqual(response.status_code, 200)
        self.assertTrue(data['success'])
        self.assertIn('category_name', data)
        self.assertIn('waste_type', data)
        self.assertIn('recommended_bin_color', data)
        self.assertIn('disposal_suggestion', data)
        self.assertIn('confidence_score', data)
        self.assertIn('image_url', data)
        self.assertTrue(data['stored_in_db'])

        # 2. Verify record exists in Database with all required columns
        with self.app.app_context():
            detections = WasteDetection.get_recent(limit=5)
            self.assertGreaterEqual(len(detections), 1)
            latest = detections[0]
            self.assertEqual(latest.category_name, data['category_name'])
            self.assertEqual(latest.waste_type, data['waste_type'])
            self.assertEqual(latest.bin_color, data['recommended_bin_color'])
            self.assertEqual(latest.disposal_suggestion, data['disposal_suggestion'])
            self.assertEqual(latest.image_path, data['image_url'])
            self.assertIsNotNone(latest.detected_at)

    def test_invalid_file_format_handling(self):
        """Test error handling when uploading non-image files."""
        text_bytes = io.BytesIO(b"Not an image file")
        response = self.client.post('/api/classify', data={
            'image': (text_bytes, 'document.txt')
        }, content_type='multipart/form-data')

        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertFalse(data['success'])

if __name__ == '__main__':
    print("Running AI Waste Classification Backend Unit Tests...\n")
    unittest.main()

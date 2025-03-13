import unittest
from flask import json
from app import app, collection
from unittest.mock import patch

class FlaskAppTestCase(unittest.TestCase):
    
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    @patch('app.collection.find_one')
    def test_home_route_get(self, mock_find_one):
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Ajio Price Tracker', response.data)  # Adjust based on actual HTML content

    @patch('app.requests.get')
    @patch('app.collection.find_one')
    @patch('app.collection.insert_one')
    def test_home_route_post(self, mock_insert_one, mock_find_one, mock_requests_get):
        mock_find_one.return_value = None  # Simulate no existing data in MongoDB
        mock_requests_get.return_value.status_code = 200
        mock_requests_get.return_value.json.return_value = {
            'baseOptions': [{'options': [{'modelImage': {'altText': 'Test Product'},
                                          'stock': {'stockLevelStatus': 'inStock', 'stockLevel': 10},
                                          'priceData': {'value': 500}}]}],
            'potentialPromotions': [{'maxSavingPrice': 50}]
        }
        
        response = self.app.post('/', data={'url': 'https://www.ajio.com/test-product'}, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Test Product', response.data)
        self.assertIn(b'500', response.data)
        
    @patch('app.requests.get', side_effect=Exception("API error"))
    def test_api_failure(self, mock_requests_get):
        response = self.app.post('/', data={'url': 'https://www.ajio.com/test-product'}, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'An unexpected error occurred', response.data)

if __name__ == '__main__':
    unittest.main()

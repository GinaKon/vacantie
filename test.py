import unittest
from unittest.mock import patch
from model import Destinations
from main import app


class DestinationsTestCase(unittest.TestCase):
    SQLALCHEMY_DATABASE_URI = "sqlite://"
    TESTING = True
    def setUp(self):
        self.app = app
        self.app.testing = True
        self.client = self.app.test_client()

        self.app_context = self.app.app_context()
        self.app_context.push()

    def tearDown(self):
        self.app_context.pop()

    @patch("main.jsonify")
    @patch("main.db.session")
    @patch("main.Destinations.query")
    def test_create_destination_new_destination_returns_response_201(self, mock_query, mock_db_session, mocked_json):
        with app.app_context():
            destination = Destinations(
                Id = "Test",
                Name = "Test",
                Temperature = "Test"
            )
            mock_query.filter_by.return_value.first.return_value = None
            mock_db_session.add.return_value = destination
            mocked_json(destination.serialize()).return_value = "Test"

            response = self.client.post('/destinations',
                                        json={'name': 'Create a destination', 'temperature': 'Temperature'})

            self.assertEqual(response.status_code, 201)



if __name__ == '__main__':
    unittest.main()

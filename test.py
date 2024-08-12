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

    def create_destination_with_missing_name_returns_response_422(self):
        with app.app_contaxt():
            response = self.client.post('/destinations',
                                        json={'name':'Name', 'temperature': 'Temperature'})

            self.assertEqual(response.status_code, 422)

    @patch('main.Destinations.query')
    def test_create_destination_with_duplicate_name_returns_response_409(self, mock_query):
        with app.app_context():
            destination = Destinations(
                Id="Test",
                Name="Test",
                Temperature="Test"
            )
            mock_query.filter_by.return_value.first.return_value = destination

            response = self.client.post('/destinations',
                                        json={'name': 'Create a destination', 'temperature':'Temperature'})

            self.assertEqual(response.status_code, 409)

    @patch('main.db.session')
    @patch('main.Destinations.query')
    def test_delete_destination_with_valid_destination_returns_response_200(self, mock_query, mock_db_session):
        with app.app_context():
            destination = Destinations(
                Id="Test",
                Name="Test",
                Temperature="Test"
            )
            mock_query.filter_by.return_value.first.return_value = destination
            mock_db_session.delete.return_value = None
            mock_db_session.commit.return_value = None

            response = self.client.delete('/destinations/Test')

            self.assertEqual(response.status_code, 200)

    def test_delete_destination_with_invalid_destination_returns_response_404(self):
        with app.app_context():
            response = self.client.delete('/destinations/Test')

            self.assertEqual(response.status_code, 404)



if __name__ == '__main__':
    unittest.main()

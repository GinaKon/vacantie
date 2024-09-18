import unittest
from unittest.mock import patch, MagicMock
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

    def test_create_destination_with_missing_name_returns_response_422(self):
        with app.app_context():
            response = self.client.post('/destinations',
                                        json={'temperature': 'Temperature'})

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

    def test_delete_destination_with_invalid_destination_name_returns_response_404(self):
        with app.app_context():
            response = self.client.delete('/destinations/Test')

            self.assertEqual(response.status_code, 404)

    @patch("main.jsonify")
    @patch("main.db.session")
    @patch("main.Destinations.query")
    def test_update_ideal_temp_returns_response_200(self, mock_query, mock_db_session, mocked_json):
        with app.app_context():
            destination_update = Destinations(
                Id = "Test",
                Name = "Test",
                Temperature = "23"
            )
            mock_query.filter_by.return_value.first.return_value = destination_update
            mock_db_session.commit.return_value = None
            mocked_json.return_value = {
                "message": "Destination temperature updated successfully",
                "updated_destination": destination_update.serialize()
            }

            response = self.client.patch('/destinations',
                                         json = {'destination_name': 'Test','new_temperature': 25})

            self.assertEqual(response.status_code, 200)

    @patch("main.db.session")
    @patch("main.Destinations.query")
    def test_update_ideal_temp_with_missing_name_returns_response_422(self, mock_query, mock_db_session):
        with app.app_context():
            response = self.client.patch('/destinations',
                                            json = {'new_temperature': 25})

            self.assertEqual(response.status_code, 422)

    @patch("main.db.session")
    @patch("main.Destinations.query")
    def test_update_ideal_temp_with_new_temp_missing_name_returns_response_422(self, mock_query, mock_db_session):
        with app.app_context():
            response = self.client.patch('/destinations',
                                         json = {'destination_name': 'Test'})

            self.assertEqual(response.status_code, 422)

    def test_update_ideal_temp_with_invalid_destination_name_returns_response_404(self):
        with app.app_context():
            response = self.client.patch('/destinations',
                                            json = {'destination_name': 'Test', 'new_temperature': 25})

            self.assertEqual(response.status_code, 404)

    @patch("main.jsonify")
    @patch("main.db.session")
    @patch("main.Destinations.query")
    def test_fetch_all_destinations_returns_response_200(self, mock_json, mock_db_session, mock_query):
        with app.app_context():
            response = self.client.get('fetch_destinations')

            self.assertEqual(response.status_code, 200)

    @patch("main.Destinations.query")
    def test_get_destination_with_valid_destination_name_returns_response_200(self,mocked_destination):
        with app.app_context():
            destination = Destinations(
                Id="Test",
                Name="Test",
                Temperature="23"
            )
            mocked_destination.filter_by.return_value.first.return_value = destination
            response = self.client.get('/get_destination?destination=Test')

            self.assertEqual(response.status_code, 200)

    def test_get_destination_with_no_destination_name_returns_response_404(self):
        with app.app_context():
            response = self.client.get('/get_destination?destination=Test')

            self.assertEqual(response.status_code, 404)

    @patch("main.requests.get")
    @patch("main.Destinations.query")
    def test_get_verdict_with_perfect_temp_returns_response_200(self, mock_query, mock_get):
        destination = Destinations(
            Id="Test",
            Name="Test",
            Temperature=25
        )
        mock_query.filter_by.return_value.first.return_value = destination

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'data': {'values': {'temperature': 25}}
        }
        mock_get.return_value = mock_response

        response = self.client.get('/get_verdict?destination=Test')

        self.assertEqual(response.status_code, 200)
        response_data = response.get_json()
        self.assertEqual(response_data['currentTemperature'], 25)
        self.assertEqual(response_data['idealTemperature'], 25)
        self.assertEqual(response_data['verdict'], 'Perfect')

    @patch("main.requests.get")
    @patch("main.Destinations.query")
    def test_get_verdict_with_high_temp_returns_too_hot(self, mock_query, mock_get):
        destination = Destinations(
            Id="Test",
            Name="Test",
            Temperature=20
        )
        mock_query.filter_by.return_value.first.return_value = destination

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'data': {'values': {'temperature': 25}}
        }
        mock_get.return_value = mock_response

        response = self.client.get('/get_verdict?destination=Test')

        self.assertEqual(response.status_code, 200)
        response_data = response.get_json()
        self.assertEqual(response_data['currentTemperature'], 25)
        self.assertEqual(response_data['idealTemperature'], 20)
        self.assertEqual(response_data['verdict'], 'Too Hot')

    @patch("main.requests.get")
    @patch("main.Destinations.query")
    def test_get_verdict_with_low_temp_returns_too_cold(self, mock_query, mock_get):
        destination = Destinations(
            Id="Test",
            Name="Test",
            Temperature=30
        )
        mock_query.filter_by.return_value.first.return_value = destination

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'data': {'values': {'temperature': 25}}
        }
        mock_get.return_value = mock_response

        response = self.client.get('/get_verdict?destination=Test')

        self.assertEqual(response.status_code, 200)
        response_data = response.get_json()
        self.assertEqual(response_data['currentTemperature'], 25)
        self.assertEqual(response_data['idealTemperature'], 30)
        self.assertEqual(response_data['verdict'], 'Too Cold')

    @patch("main.requests.get")
    @patch("main.Destinations.query")
    def test_get_verdict_destination_not_found(self, mock_query, mock_get):
        mock_query.filter_by.return_value.first.return_value = None

        response = self.client.get('/get_verdict?destination=NonExistent')

        self.assertEqual(response.status_code, 404)
        response_data = response.get_json()
        self.assertEqual(response_data['error'], 'Destination not found')

    @patch("main.requests.get")
    @patch("main.Destinations.query")
    def test_get_verdict_api_failure(self, mock_query, mock_get):
        destination = Destinations(
            Id="Test",
            Name="Test",
            Temperature=25
        )
        mock_query.filter_by.return_value.first.return_value = destination

        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_get.return_value = mock_response

        response = self.client.get('/get_verdict?destination=Test')

        self.assertEqual(response.status_code, 500)
        response_data = response.get_json()
        self.assertEqual(response_data['error'], 'Failed to get data from API')


if __name__ == '__main__':
    unittest.main()

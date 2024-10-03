import unittest
from src.main import app


class StatusEndpointTestCase(unittest.TestCase):
    def setUp(self):
        # Set up the Flask test client
        self.app = app.test_client()
        self.app.testing = True

    def test_status_endpoint(self):
        # Send a GET request to the /status endpoint
        response = self.app.get("/status")

        # Assert the response status code
        self.assertEqual(response.status_code, 200)

        # Parse the JSON response data
        response_data = response.get_json()

        # Check the structure of the response
        self.assertIn("status", response_data)
        self.assertIn("message", response_data)

        # Verify the values
        self.assertEqual(response_data["status"], "OK")
        self.assertEqual(
            response_data["message"], "The application is running smoothly"
        )


if __name__ == "__main__":
    unittest.main()

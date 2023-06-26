import unittest
import json
from app import app
from unittest.mock import patch

class FlaskTestCase(unittest.TestCase):

    def setUp(self):
        self.app = app
        self.client = self.app.test_client()

    @patch('app.comments')  # Replace with the actual path of the function in your project
    def test_post_comments(self, mock_process_comments):
        mock_process_comments.return_value = None  # Replace with the value you expect from process_comments()

        payload = {
            'number': '50',  # Replace with a test number
            'url': 'https://www.youtube.com/watch?v=bsWZF7g2R-Q'  # Replace with a test url
        }

        response = self.client.post('/comments', data=json.dumps(payload), content_type='application/json')

        self.assertEqual(response.status_code, 200)
        mock_process_comments.assert_called_once_with(payload['url'], payload['number'], any)  # The any placeholder is for the job_id which is generated dynamically in the function

    def tearDown(self):
        pass

if __name__ == "__main__":
    unittest.main()

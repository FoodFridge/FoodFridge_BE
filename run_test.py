import unittest
from unittest.mock import patch
from run import lambda_handler

class TestLambdaHandler(unittest.TestCase):
    @patch('run.awsgi.response')
    def test_awsgi_response_called(self, mock_awsgi_response):
        lambda_handler({'some': 'event'}, {'some': 'context'})
        mock_awsgi_response.assert_called()

if __name__ == "__main__":
    unittest.main()

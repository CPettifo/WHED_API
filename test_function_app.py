import os
import sys
import unittest
from unittest.mock import MagicMock, patch
import json
import types

# Set environment variables
os.environ["MYSQL_HOST"] = "localhost"
os.environ["MYSQL_USER"] = "user"
os.environ["MYSQL_PASSWORD"] = "password"
os.environ["MYSQL_DATABASE"] = "database"

# Create a custom mock azure.functions module
azure_functions_module = types.ModuleType('azure.functions')

class HttpResponse:
    def __init__(self, body=None, status_code=200):
        if isinstance(body, str):
            self._body = body.encode()
        elif isinstance(body, bytes):
            self._body = body
        elif body is None:
            self._body = b''
        else:
            self._body = json.dumps(body).encode()
        self.status_code = status_code

    def get_body(self):
        return self._body

class HttpRequest:
    def __init__(self, method='GET', url='', headers=None, params=None, route_params=None, body=None):
        self.method = method
        self.url = url
        self.headers = headers or {}
        self.params = params or {}
        self.route_params = route_params or {}
        self._body = body

    def get_json(self):
        return json.loads(self._body) if self._body else {}

class FunctionApp:
    def __init__(self):
        pass

    def route(self, **kwargs):
        def decorator(f):
            return f
        return decorator

azure_functions_module.HttpResponse = HttpResponse
azure_functions_module.HttpRequest = HttpRequest
azure_functions_module.FunctionApp = FunctionApp
azure_functions_module.AuthLevel = MagicMock()
azure_functions_module.AuthLevel.ANONYMOUS = MagicMock()

# Assign the custom module to sys.modules
sys.modules['azure.functions'] = azure_functions_module

# Mock other external libraries
sys.modules['mysql'] = MagicMock()
sys.modules['mysql.connector'] = MagicMock()
sys.modules['mysql.connector.pooling'] = MagicMock()
sys.modules['auth0.authentication'] = MagicMock()
sys.modules['dotenv'] = MagicMock()
sys.modules['auth'] = MagicMock()

# Mock the auth.protected decorator
def mock_protected(func):
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper

sys.modules['auth'].protected = mock_protected

# Import your module after mocking
import function_app  # Replace with your actual module name if different

# Write your test cases
class TestGetCurrencies(unittest.TestCase):
    @patch('function_app.db_pool')
    def test_get_currencies_success(self, mock_db_pool):
        # Mock the database connection and cursor
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [
            {'currency_name': 'Dollar', 'currency_code': 'USD'},
            {'currency_name': 'Euro', 'currency_code': 'EUR'}
        ]

        mock_connection = MagicMock()
        mock_connection.cursor.return_value.__enter__.return_value = mock_cursor
        mock_db_pool.get_connection.return_value.__enter__.return_value = mock_connection

        # Mock HttpRequest and current_user
        mock_req = HttpRequest()
        current_user = MagicMock()

        # Call the function
        response = function_app.get_currencies(mock_req, current_user)

        # Assertions
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            json.loads(response.get_body().decode()),
            [
                {'currency_name': 'Dollar', 'currency_code': 'USD'},
                {'currency_name': 'Euro', 'currency_code': 'EUR'}
            ]
        )

class TestDeleteCurrency(unittest.TestCase):
    @patch('function_app.db_pool')
    def test_delete_currency_success(self, mock_db_pool):
        # Mock the database connection and cursor
        mock_cursor = MagicMock()
        mock_connection = MagicMock()
        mock_connection.cursor.return_value.__enter__.return_value = mock_cursor
        mock_db_pool.get_connection.return_value.__enter__.return_value = mock_connection

        # Mock HttpRequest with valid currency_code
        mock_req = HttpRequest()
        mock_req.route_params = {'currency_code': 'USD'}
        current_user = MagicMock()

        # Call the function
        response = function_app.delete_currency(mock_req, current_user)

        # Assertions
        self.assertEqual(response.status_code, 204)

    def test_delete_currency_invalid_code(self):
        # Mock HttpRequest with invalid currency_code
        mock_req = HttpRequest()
        mock_req.route_params = {'currency_code': '12'}
        current_user = MagicMock()

        # Call the function
        response = function_app.delete_currency(mock_req, current_user)

        # Assertions
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.get_body().decode(),
            'currency_code should be three capitalized alphabetic characters'
        )

class TestPostCurrency(unittest.TestCase):
    @patch('function_app.db_pool')
    def test_post_currency_success(self, mock_db_pool):
        # Mock the database connection and cursor
        mock_cursor = MagicMock()
        mock_connection = MagicMock()
        mock_connection.cursor.return_value.__enter__.return_value = mock_cursor
        mock_db_pool.get_connection.return_value.__enter__.return_value = mock_connection

        # Mock HttpRequest with valid data
        request_body = json.dumps({
            'currency_name': 'Pound',
            'currency_code': 'GBP'
        })
        mock_req = HttpRequest(method='POST', body=request_body)
        current_user = MagicMock()

        # Call the function
        response = function_app.post_currency(mock_req, current_user)

        # Assertions
        self.assertEqual(response.status_code, 201)

    def test_post_currency_missing_name(self):
        # Mock HttpRequest with missing currency_name
        request_body = json.dumps({
            'currency_code': 'GBP'
        })
        mock_req = HttpRequest(method='POST', body=request_body)
        current_user = MagicMock()

        # Call the function
        response = function_app.post_currency(mock_req, current_user)

        # Assertions
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.get_body().decode(),
            'currency_name is required'
        )

class TestAuthenticate(unittest.TestCase):
    @patch('function_app.GetToken')
    def test_authenticate_success(self, mock_get_token):
        # Mock GetToken instance and login method
        mock_get_token_instance = MagicMock()
        mock_get_token_instance.login.return_value = {'access_token': 'fake_token'}
        mock_get_token.return_value = mock_get_token_instance

        # Mock HttpRequest with valid credentials
        request_body = json.dumps({
            'username': 'user',
            'password': 'pass'
        })
        mock_req = HttpRequest(method='POST', body=request_body)

        # Call the function
        response = function_app.authenticate(mock_req)

        # Assertions
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            json.loads(response.get_body().decode()),
            {'access_token': 'fake_token'}
        )

    @patch('function_app.GetToken')
    def test_authenticate_failure(self, mock_get_token):
        # Simulate authentication failure
        mock_get_token_instance = MagicMock()
        mock_get_token_instance.login.side_effect = Exception('Invalid credentials')
        mock_get_token.return_value = mock_get_token_instance

        # Mock HttpRequest with invalid credentials
        request_body = json.dumps({
            'username': 'user',
            'password': 'wrong_pass'
        })
        mock_req = HttpRequest(method='POST', body=request_body)

        # Call the function
        response = function_app.authenticate(mock_req)

        # Assertions
        self.assertEqual(response.status_code, 500)
        self.assertEqual(
            response.get_body().decode(),
            'Internal Error'
        )

if __name__ == '__main__':
    unittest.main()





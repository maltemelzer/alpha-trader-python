"""Unit tests for error handling in the Alpha Trader Client.

These tests use mocking to simulate API responses without requiring real credentials.
"""
import pytest
from unittest.mock import Mock, patch

from alpha_trader.client import Client
from alpha_trader.exceptions import (
    AuthenticationError,
    NotAuthenticatedError,
    APIError,
    NotFoundError,
    ValidationError,
    PermissionError as APIPermissionError,
)


@pytest.fixture
def client():
    """Create a client instance for testing."""
    return Client(
        base_url="https://api.example.com",
        username="testuser",
        password="testpass",
        partner_id="test-partner-id",
    )


class TestClientInitialization:
    """Tests for Client initialization."""

    def test_client_creation(self, client):
        """Test that a client can be created with valid parameters."""
        assert client.base_url == "https://api.example.com"
        assert client.username == "testuser"
        assert client.password == "testpass"
        assert client.partner_id == "test-partner-id"
        assert client.authenticated is False
        assert client.token is None

    def test_client_requires_base_url(self):
        """Test that client creation fails without base_url."""
        with pytest.raises(Exception):  # Pydantic validation error
            Client(
                base_url=None,
                username="testuser",
                password="testpass",
                partner_id="test-partner-id",
            )


class TestLogin:
    """Tests for the login method."""

    @patch("alpha_trader.client.requests.request")
    def test_login_success(self, mock_request, client):
        """Test successful login."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"message": "test-token-123"}
        mock_request.return_value = mock_response

        token = client.login()

        assert token == "test-token-123"
        assert client.token == "test-token-123"
        assert client.authenticated is True
        mock_request.assert_called_once()

    @patch("alpha_trader.client.requests.request")
    def test_login_invalid_credentials(self, mock_request, client):
        """Test login with invalid credentials returns 401."""
        mock_response = Mock()
        mock_response.status_code = 401
        mock_request.return_value = mock_response

        with pytest.raises(AuthenticationError) as exc_info:
            client.login()

        assert exc_info.value.status_code == 401
        assert "Invalid credentials" in str(exc_info.value)
        assert client.authenticated is False

    @patch("alpha_trader.client.requests.request")
    def test_login_forbidden(self, mock_request, client):
        """Test login with invalid partner ID returns 403."""
        mock_response = Mock()
        mock_response.status_code = 403
        mock_request.return_value = mock_response

        with pytest.raises(AuthenticationError) as exc_info:
            client.login()

        assert exc_info.value.status_code == 403
        assert "forbidden" in str(exc_info.value).lower()

    @patch("alpha_trader.client.requests.request")
    def test_login_server_error(self, mock_request, client):
        """Test login with server error."""
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.text = "Internal Server Error"
        mock_request.return_value = mock_response

        with pytest.raises(AuthenticationError) as exc_info:
            client.login()

        assert exc_info.value.status_code == 500

    @patch("alpha_trader.client.requests.request")
    def test_login_invalid_response_format(self, mock_request, client):
        """Test login with invalid response format."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"unexpected": "format"}
        mock_request.return_value = mock_response

        with pytest.raises(AuthenticationError) as exc_info:
            client.login()

        assert "Invalid response" in str(exc_info.value)


class TestRequest:
    """Tests for the request method."""

    @patch("alpha_trader.client.requests.request")
    def test_request_not_authenticated(self, mock_request, client):
        """Test that request fails when not authenticated."""
        with pytest.raises(NotAuthenticatedError) as exc_info:
            client.request("GET", "api/test")

        assert "not authenticated" in str(exc_info.value).lower()
        mock_request.assert_not_called()

    @patch("alpha_trader.client.requests.request")
    def test_request_success(self, mock_request, client):
        """Test successful authenticated request."""
        # First, mock successful login
        mock_login_response = Mock()
        mock_login_response.status_code = 200
        mock_login_response.json.return_value = {"message": "test-token"}

        mock_api_response = Mock()
        mock_api_response.status_code = 200
        mock_api_response.json.return_value = {"data": "test"}

        mock_request.side_effect = [mock_login_response, mock_api_response]

        client.login()
        response = client.request("GET", "api/test")

        assert response.status_code == 200

    @patch("alpha_trader.client.requests.request")
    def test_request_not_found(self, mock_request, client):
        """Test that 404 response raises NotFoundError."""
        mock_login_response = Mock()
        mock_login_response.status_code = 200
        mock_login_response.json.return_value = {"message": "test-token"}

        mock_api_response = Mock()
        mock_api_response.status_code = 404
        mock_api_response.json.return_value = {"message": "Resource not found"}

        mock_request.side_effect = [mock_login_response, mock_api_response]

        client.login()

        with pytest.raises(NotFoundError) as exc_info:
            client.request("GET", "api/nonexistent")

        assert exc_info.value.status_code == 404
        assert exc_info.value.endpoint == "api/nonexistent"

    @patch("alpha_trader.client.requests.request")
    def test_request_validation_error(self, mock_request, client):
        """Test that 400 response raises ValidationError."""
        mock_login_response = Mock()
        mock_login_response.status_code = 200
        mock_login_response.json.return_value = {"message": "test-token"}

        mock_api_response = Mock()
        mock_api_response.status_code = 400
        mock_api_response.json.return_value = {"message": "Invalid parameters"}

        mock_request.side_effect = [mock_login_response, mock_api_response]

        client.login()

        with pytest.raises(ValidationError) as exc_info:
            client.request("POST", "api/orders", json={"invalid": "data"})

        assert exc_info.value.status_code == 400

    @patch("alpha_trader.client.requests.request")
    def test_request_permission_denied(self, mock_request, client):
        """Test that 403 response raises PermissionError."""
        mock_login_response = Mock()
        mock_login_response.status_code = 200
        mock_login_response.json.return_value = {"message": "test-token"}

        mock_api_response = Mock()
        mock_api_response.status_code = 403
        mock_api_response.json.return_value = {"message": "Permission denied"}

        mock_request.side_effect = [mock_login_response, mock_api_response]

        client.login()

        with pytest.raises(APIPermissionError) as exc_info:
            client.request("DELETE", "api/protected-resource")

        assert exc_info.value.status_code == 403

    @patch("alpha_trader.client.requests.request")
    def test_request_auth_expired(self, mock_request, client):
        """Test that 401 response during request raises AuthenticationError."""
        mock_login_response = Mock()
        mock_login_response.status_code = 200
        mock_login_response.json.return_value = {"message": "test-token"}

        mock_api_response = Mock()
        mock_api_response.status_code = 401
        mock_api_response.json.return_value = {"message": "Token expired"}

        mock_request.side_effect = [mock_login_response, mock_api_response]

        client.login()

        with pytest.raises(AuthenticationError) as exc_info:
            client.request("GET", "api/user")

        assert exc_info.value.status_code == 401

    @patch("alpha_trader.client.requests.request")
    def test_request_server_error(self, mock_request, client):
        """Test that 500 response raises APIError."""
        mock_login_response = Mock()
        mock_login_response.status_code = 200
        mock_login_response.json.return_value = {"message": "test-token"}

        mock_api_response = Mock()
        mock_api_response.status_code = 500
        mock_api_response.json.return_value = {"message": "Internal error"}

        mock_request.side_effect = [mock_login_response, mock_api_response]

        client.login()

        with pytest.raises(APIError) as exc_info:
            client.request("GET", "api/test")

        assert exc_info.value.status_code == 500

    @patch("alpha_trader.client.requests.request")
    def test_request_no_raise_for_status(self, mock_request, client):
        """Test that errors are not raised when raise_for_status=False."""
        mock_login_response = Mock()
        mock_login_response.status_code = 200
        mock_login_response.json.return_value = {"message": "test-token"}

        mock_api_response = Mock()
        mock_api_response.status_code = 404
        mock_api_response.json.return_value = {"message": "Not found"}

        mock_request.side_effect = [mock_login_response, mock_api_response]

        client.login()
        response = client.request("GET", "api/missing", raise_for_status=False)

        assert response.status_code == 404

    @patch("alpha_trader.client.requests.request")
    def test_request_with_additional_headers(self, mock_request, client):
        """Test that additional headers are merged correctly."""
        mock_login_response = Mock()
        mock_login_response.status_code = 200
        mock_login_response.json.return_value = {"message": "test-token"}

        mock_api_response = Mock()
        mock_api_response.status_code = 200

        mock_request.side_effect = [mock_login_response, mock_api_response]

        client.login()
        client.request("POST", "api/test", additional_headers={"X-Custom": "value"})

        # Check that the second call included the custom header
        call_args = mock_request.call_args_list[1]
        headers = call_args.kwargs["headers"]
        assert "Authorization" in headers
        assert headers["X-Custom"] == "value"


class TestBuildUrl:
    """Tests for URL building."""

    def test_build_url_with_trailing_slash(self, client):
        """Test URL building when base URL has trailing slash."""
        client.base_url = "https://api.example.com/"
        url = client._build_url("api/test")
        assert url == "https://api.example.com/api/test"

    def test_build_url_without_trailing_slash(self, client):
        """Test URL building when base URL has no trailing slash."""
        client.base_url = "https://api.example.com"
        url = client._build_url("api/test")
        assert url == "https://api.example.com/api/test"

    def test_build_url_with_endpoint_slash(self, client):
        """Test URL building when endpoint has leading slash."""
        client.base_url = "https://api.example.com"
        url = client._build_url("/api/test")
        assert url == "https://api.example.com/api/test"


class TestExceptionHierarchy:
    """Tests for exception hierarchy."""

    def test_all_exceptions_inherit_from_base(self):
        """Test that all custom exceptions inherit from AlphaTraderError."""
        from alpha_trader.exceptions import AlphaTraderError

        assert issubclass(AuthenticationError, AlphaTraderError)
        assert issubclass(NotAuthenticatedError, AlphaTraderError)
        assert issubclass(APIError, AlphaTraderError)
        assert issubclass(NotFoundError, AlphaTraderError)
        assert issubclass(ValidationError, AlphaTraderError)
        assert issubclass(APIPermissionError, AlphaTraderError)

    def test_api_error_hierarchy(self):
        """Test that specific API errors inherit from APIError."""
        assert issubclass(NotFoundError, APIError)
        assert issubclass(ValidationError, APIError)
        assert issubclass(APIPermissionError, APIError)

    def test_api_error_message_format(self):
        """Test that APIError formats message correctly."""
        error = APIError("Test error", status_code=500, endpoint="api/test")
        assert "500" in str(error)
        assert "Test error" in str(error)

    def test_authentication_error_attributes(self):
        """Test AuthenticationError has expected attributes."""
        error = AuthenticationError("Login failed", status_code=401)
        assert error.status_code == 401
        assert "Login failed" in str(error)

    def test_not_found_error_attributes(self):
        """Test NotFoundError has expected attributes."""
        error = NotFoundError("User not found", endpoint="api/users/123")
        assert error.status_code == 404
        assert error.endpoint == "api/users/123"

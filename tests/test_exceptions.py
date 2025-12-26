"""Unit tests for the Alpha Trader exceptions module."""
import pytest

from alpha_trader.exceptions import (
    AlphaTraderError,
    AuthenticationError,
    NotAuthenticatedError,
    APIError,
    NotFoundError,
    ValidationError,
    PermissionError as APIPermissionError,
    InsufficientFundsError,
    OrderError,
    ResourceStateError,
)


class TestAlphaTraderError:
    """Tests for the base AlphaTraderError."""

    def test_is_exception(self):
        """Test that AlphaTraderError is an Exception."""
        assert issubclass(AlphaTraderError, Exception)

    def test_can_be_raised(self):
        """Test that AlphaTraderError can be raised and caught."""
        with pytest.raises(AlphaTraderError):
            raise AlphaTraderError("Test error")


class TestAuthenticationError:
    """Tests for AuthenticationError."""

    def test_default_message(self):
        """Test default message."""
        error = AuthenticationError()
        assert "Authentication failed" in str(error)

    def test_custom_message(self):
        """Test custom message."""
        error = AuthenticationError("Invalid token")
        assert "Invalid token" in str(error)

    def test_status_code(self):
        """Test status code attribute."""
        error = AuthenticationError("Failed", status_code=401)
        assert error.status_code == 401

    def test_status_code_none(self):
        """Test status code is None by default."""
        error = AuthenticationError("Failed")
        assert error.status_code is None

    def test_inherits_from_base(self):
        """Test inheritance from AlphaTraderError."""
        assert issubclass(AuthenticationError, AlphaTraderError)

    def test_catchable_as_base(self):
        """Test can be caught as AlphaTraderError."""
        with pytest.raises(AlphaTraderError):
            raise AuthenticationError("Failed")


class TestNotAuthenticatedError:
    """Tests for NotAuthenticatedError."""

    def test_default_message(self):
        """Test default message."""
        error = NotAuthenticatedError()
        assert "not authenticated" in str(error).lower()
        assert "login()" in str(error)

    def test_custom_message(self):
        """Test custom message."""
        error = NotAuthenticatedError("Please authenticate first")
        assert "Please authenticate first" in str(error)

    def test_inherits_from_base(self):
        """Test inheritance from AlphaTraderError."""
        assert issubclass(NotAuthenticatedError, AlphaTraderError)


class TestAPIError:
    """Tests for APIError."""

    def test_message_format(self):
        """Test message includes status code and message."""
        error = APIError("Something went wrong", status_code=500)
        assert "500" in str(error)
        assert "Something went wrong" in str(error)

    def test_status_code_attribute(self):
        """Test status_code attribute."""
        error = APIError("Error", status_code=503)
        assert error.status_code == 503

    def test_response_attribute(self):
        """Test response attribute."""
        response_data = {"error": "details", "code": 123}
        error = APIError("Error", status_code=500, response=response_data)
        assert error.response == response_data

    def test_endpoint_attribute(self):
        """Test endpoint attribute."""
        error = APIError("Error", status_code=500, endpoint="api/users")
        assert error.endpoint == "api/users"

    def test_all_attributes(self):
        """Test all attributes together."""
        error = APIError(
            "Database error",
            status_code=500,
            response={"detail": "Connection failed"},
            endpoint="api/data"
        )
        assert error.status_code == 500
        assert error.response == {"detail": "Connection failed"}
        assert error.endpoint == "api/data"


class TestNotFoundError:
    """Tests for NotFoundError."""

    def test_inherits_from_api_error(self):
        """Test inheritance from APIError."""
        assert issubclass(NotFoundError, APIError)

    def test_status_code_is_404(self):
        """Test status code is always 404."""
        error = NotFoundError()
        assert error.status_code == 404

    def test_default_message(self):
        """Test default message."""
        error = NotFoundError()
        assert "not found" in str(error).lower()

    def test_custom_message(self):
        """Test custom message."""
        error = NotFoundError("User with ID 123 not found")
        assert "User with ID 123 not found" in str(error)

    def test_endpoint_attribute(self):
        """Test endpoint attribute."""
        error = NotFoundError(endpoint="api/users/123")
        assert error.endpoint == "api/users/123"


class TestValidationError:
    """Tests for ValidationError."""

    def test_inherits_from_api_error(self):
        """Test inheritance from APIError."""
        assert issubclass(ValidationError, APIError)

    def test_status_code_is_400(self):
        """Test status code is always 400."""
        error = ValidationError()
        assert error.status_code == 400

    def test_default_message(self):
        """Test default message."""
        error = ValidationError()
        assert "validation" in str(error).lower()

    def test_custom_message(self):
        """Test custom message."""
        error = ValidationError("Email format is invalid")
        assert "Email format is invalid" in str(error)

    def test_response_with_validation_details(self):
        """Test response contains validation details."""
        details = {"email": "Invalid format", "age": "Must be positive"}
        error = ValidationError("Validation failed", response=details)
        assert error.response == details


class TestAPIPermissionError:
    """Tests for APIPermissionError (PermissionError)."""

    def test_inherits_from_api_error(self):
        """Test inheritance from APIError."""
        assert issubclass(APIPermissionError, APIError)

    def test_status_code_is_403(self):
        """Test status code is always 403."""
        error = APIPermissionError()
        assert error.status_code == 403

    def test_default_message(self):
        """Test default message."""
        error = APIPermissionError()
        assert "permission" in str(error).lower() or "denied" in str(error).lower()


class TestInsufficientFundsError:
    """Tests for InsufficientFundsError."""

    def test_inherits_from_base(self):
        """Test inheritance from AlphaTraderError."""
        assert issubclass(InsufficientFundsError, AlphaTraderError)

    def test_default_message(self):
        """Test default message."""
        error = InsufficientFundsError()
        assert "insufficient funds" in str(error).lower()

    def test_custom_message(self):
        """Test custom message."""
        error = InsufficientFundsError("Need $100 more for this order")
        assert "Need $100 more" in str(error)


class TestOrderError:
    """Tests for OrderError."""

    def test_inherits_from_base(self):
        """Test inheritance from AlphaTraderError."""
        assert issubclass(OrderError, AlphaTraderError)

    def test_message(self):
        """Test message."""
        error = OrderError("Order execution failed")
        assert "Order execution failed" in str(error)

    def test_check_result_attribute(self):
        """Test check_result attribute."""
        check_result = {"status": "FAILED", "reason": "Market closed"}
        error = OrderError("Order failed", check_result=check_result)
        assert error.check_result == check_result

    def test_check_result_none(self):
        """Test check_result is None by default."""
        error = OrderError("Order failed")
        assert error.check_result is None


class TestResourceStateError:
    """Tests for ResourceStateError."""

    def test_inherits_from_base(self):
        """Test inheritance from AlphaTraderError."""
        assert issubclass(ResourceStateError, AlphaTraderError)

    def test_message(self):
        """Test message."""
        error = ResourceStateError("Achievement already claimed")
        assert "Achievement already claimed" in str(error)


class TestExceptionCatching:
    """Tests for exception catching scenarios."""

    def test_catch_all_alpha_trader_errors(self):
        """Test that all errors can be caught with base class."""
        errors = [
            AuthenticationError("Auth failed"),
            NotAuthenticatedError(),
            APIError("API error", status_code=500),
            NotFoundError("Not found"),
            ValidationError("Invalid"),
            APIPermissionError("Denied"),
            InsufficientFundsError(),
            OrderError("Order failed"),
            ResourceStateError("Bad state"),
        ]

        for error in errors:
            with pytest.raises(AlphaTraderError):
                raise error

    def test_catch_api_errors_only(self):
        """Test that API errors can be caught together."""
        api_errors = [
            APIError("Generic", status_code=500),
            NotFoundError("Not found"),
            ValidationError("Invalid"),
            APIPermissionError("Denied"),
        ]

        for error in api_errors:
            with pytest.raises(APIError):
                raise error

        # These should NOT be caught as APIError
        non_api_errors = [
            AuthenticationError("Auth failed"),
            NotAuthenticatedError(),
            InsufficientFundsError(),
            OrderError("Failed"),
            ResourceStateError("Bad state"),
        ]

        for error in non_api_errors:
            with pytest.raises(AlphaTraderError):
                try:
                    raise error
                except APIError:
                    pytest.fail(f"{type(error).__name__} should not be caught as APIError")
                except AlphaTraderError:
                    raise

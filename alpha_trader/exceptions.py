"""
Custom exceptions for the Alpha Trader API client.

This module provides a hierarchy of exceptions for handling various error
conditions that may occur when interacting with the Alpha Trader API.
"""

from typing import Any, Dict, Optional


class AlphaTraderError(Exception):
    """
    Base exception for all Alpha Trader API errors.

    All custom exceptions in this module inherit from this class,
    allowing users to catch all Alpha Trader errors with a single except clause.
    """

    pass


class AuthenticationError(AlphaTraderError):
    """
    Raised when authentication fails.

    This can occur when:
    - Invalid credentials are provided
    - The token has expired
    - The partner ID is invalid
    """

    def __init__(self, message: str = "Authentication failed", status_code: Optional[int] = None):
        self.status_code = status_code
        super().__init__(message)


class NotAuthenticatedError(AlphaTraderError):
    """
    Raised when an API request is made without authentication.

    This occurs when attempting to make requests before calling login().
    """

    def __init__(self, message: str = "Client is not authenticated. Please call login() first."):
        super().__init__(message)


class APIError(AlphaTraderError):
    """
    Raised when the API returns an error response.

    Attributes:
        status_code: HTTP status code from the response
        message: Error message
        response: The full response data (if available)
        endpoint: The API endpoint that was called
    """

    def __init__(
        self,
        message: str,
        status_code: int,
        response: Optional[Dict[str, Any]] = None,
        endpoint: Optional[str] = None,
    ):
        self.status_code = status_code
        self.response = response
        self.endpoint = endpoint
        super().__init__(f"API Error ({status_code}): {message}")


class NotFoundError(APIError):
    """
    Raised when a requested resource is not found (HTTP 404).
    """

    def __init__(
        self,
        message: str = "Resource not found",
        response: Optional[Dict[str, Any]] = None,
        endpoint: Optional[str] = None,
    ):
        super().__init__(message, status_code=404, response=response, endpoint=endpoint)


class ValidationError(APIError):
    """
    Raised when the API returns a validation error (HTTP 400).

    This typically occurs when request parameters are invalid.
    """

    def __init__(
        self,
        message: str = "Validation error",
        response: Optional[Dict[str, Any]] = None,
        endpoint: Optional[str] = None,
    ):
        super().__init__(message, status_code=400, response=response, endpoint=endpoint)


class PermissionError(APIError):
    """
    Raised when the user doesn't have permission to perform an action (HTTP 403).
    """

    def __init__(
        self,
        message: str = "Permission denied",
        response: Optional[Dict[str, Any]] = None,
        endpoint: Optional[str] = None,
    ):
        super().__init__(message, status_code=403, response=response, endpoint=endpoint)


class InsufficientFundsError(AlphaTraderError):
    """
    Raised when an operation fails due to insufficient funds.

    This is a domain-specific error that can occur during trading operations.
    """

    def __init__(self, message: str = "Insufficient funds for this operation"):
        super().__init__(message)


class OrderError(AlphaTraderError):
    """
    Raised when an order operation fails.

    Attributes:
        check_result: The order check result if available
    """

    def __init__(self, message: str, check_result: Optional[Dict[str, Any]] = None):
        self.check_result = check_result
        super().__init__(message)


class ResourceStateError(AlphaTraderError):
    """
    Raised when an operation cannot be performed due to the current state of a resource.

    Examples:
    - Trying to claim an already claimed achievement
    - Trying to delete an already executed order
    """

    def __init__(self, message: str):
        super().__init__(message)

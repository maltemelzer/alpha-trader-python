__version__ = "0.6.3"

from alpha_trader.exceptions import (
    AlphaTraderError,
    AuthenticationError,
    NotAuthenticatedError,
    APIError,
    NotFoundError,
    ValidationError,
    PermissionError,
    InsufficientFundsError,
    OrderError,
    ResourceStateError,
)

__all__ = [
    "__version__",
    "AlphaTraderError",
    "AuthenticationError",
    "NotAuthenticatedError",
    "APIError",
    "NotFoundError",
    "ValidationError",
    "PermissionError",
    "InsufficientFundsError",
    "OrderError",
    "ResourceStateError",
]

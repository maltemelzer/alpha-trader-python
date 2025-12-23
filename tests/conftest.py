"""
Pytest configuration and fixtures for Alpha Trader tests.

This module provides shared fixtures for integration tests that require
authentication with the Alpha Trader API.

Environment Variables Required:
    BASE_URL: The base URL of the Alpha Trader API
    USERNAME: Username for authentication
    PASSWORD: Password for authentication
    PARTNER_ID: Partner ID for authentication
"""

import os
import pytest
from alpha_trader.client import Client


@pytest.fixture(scope="session")
def api_credentials():
    """Get API credentials from environment variables.

    Returns:
        dict: Dictionary containing base_url, username, password, and partner_id

    Raises:
        pytest.skip: If any required environment variable is missing
    """
    base_url = os.getenv("BASE_URL")
    username = os.getenv("USERNAME")
    password = os.getenv("PASSWORD")
    partner_id = os.getenv("PARTNER_ID")

    if not all([base_url, username, password, partner_id]):
        pytest.skip(
            "Missing required environment variables: BASE_URL, USERNAME, PASSWORD, PARTNER_ID"
        )

    return {
        "base_url": base_url,
        "username": username,
        "password": password,
        "partner_id": partner_id,
    }


@pytest.fixture(scope="session")
def client(api_credentials):
    """Create an unauthenticated client.

    Args:
        api_credentials: Fixture providing API credentials

    Returns:
        Client: An unauthenticated Alpha Trader client
    """
    return Client(
        base_url=api_credentials["base_url"],
        username=api_credentials["username"],
        password=api_credentials["password"],
        partner_id=api_credentials["partner_id"],
    )


@pytest.fixture(scope="session")
def authenticated_client(client):
    """Create an authenticated client.

    This fixture logs in once per test session for efficiency.

    Args:
        client: Fixture providing an unauthenticated client

    Returns:
        Client: An authenticated Alpha Trader client
    """
    client.login()
    return client


@pytest.fixture(scope="session")
def user(authenticated_client):
    """Get the current user.

    Args:
        authenticated_client: Fixture providing an authenticated client

    Returns:
        User: The authenticated user
    """
    return authenticated_client.get_user()


@pytest.fixture(scope="session")
def securities_account(user):
    """Get the user's securities account.

    Args:
        user: Fixture providing the authenticated user

    Returns:
        SecuritiesAccount: The user's securities account
    """
    return user.securities_account


@pytest.fixture(scope="session")
def miner(authenticated_client):
    """Get the user's miner.

    Args:
        authenticated_client: Fixture providing an authenticated client

    Returns:
        Miner: The user's miner
    """
    return authenticated_client.get_miner()

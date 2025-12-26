"""Integration tests for User functionality.

These tests require real API credentials to be set as environment variables.
They will be skipped if credentials are not available.
"""
from alpha_trader.client import Client
import os
import pytest


# Check if credentials are available
def credentials_available():
    return all([
        os.getenv("BASE_URL"),
        os.getenv("USERNAME"),
        os.getenv("PASSWORD"),
        os.getenv("PARTNER_ID"),
    ])


requires_credentials = pytest.mark.skipif(
    not credentials_available(),
    reason="API credentials not available (BASE_URL, USERNAME, PASSWORD, PARTNER_ID)"
)


@pytest.fixture
def authenticated_client():
    """Fixture that provides an authenticated client."""
    client = Client(
        base_url=os.getenv("BASE_URL"),
        username=os.getenv("USERNAME"),
        password=os.getenv("PASSWORD"),
        partner_id=os.getenv("PARTNER_ID"),
    )
    client.login()
    return client


@requires_credentials
def test_user_initialization(authenticated_client):
    user = authenticated_client.get_user()

    assert user.id is not None
    assert user.username == os.getenv("USERNAME")
    assert user.email is not None
    assert user.jwt_token is not None


@requires_credentials
def test_achievements(authenticated_client):
    user = authenticated_client.get_user()

    assert user.achievements is not None
    assert user.achievements[0].claimed is False


@requires_credentials
def test_securities_account(authenticated_client):
    user = authenticated_client.get_user()

    assert user.securities_account is not None
    assert user.securities_account.private_account
    assert user.securities_account.id is not None
    assert user.securities_account.clearing_account_id is not None

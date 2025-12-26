"""Integration tests for the Alpha Trader Client.

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
def test_login():
    client = Client(
        base_url=os.getenv("BASE_URL"),
        username=os.getenv("USERNAME"),
        password=os.getenv("PASSWORD"),
        partner_id=os.getenv("PARTNER_ID"),
    )

    client.login()

    assert client.authenticated is True
    assert client.token is not None


@requires_credentials
def test_get_user(authenticated_client):
    user = authenticated_client.get_user()

    assert user.id is not None
    assert user.username is not None
    assert user.email is not None
    assert user.jwt_token is not None


@requires_credentials
def test_get_miner(authenticated_client):
    miner = authenticated_client.get_miner()

    assert miner.id is not None
    assert miner.coins_per_hour is not None
    assert miner.transferable_coins == 1


@requires_credentials
def test_get_listing(authenticated_client):
    listing = authenticated_client.get_listing("ACALPHCOIN")

    assert listing.end_date is None
    assert listing.name == "AlphaCoins"
    assert listing.security_identifier == "ACALPHCOIN"
    assert listing.type == "COIN"


@requires_credentials
def test_get_price_spread(authenticated_client):
    price_spread = authenticated_client.get_price_spread("ACALPHCOIN")

    assert price_spread.security_identifier == "ACALPHCOIN"
    assert price_spread.listing.security_identifier == "ACALPHCOIN"
    assert price_spread.last_price is not None


@requires_credentials
def test_get_securities_account(authenticated_client):
    user = authenticated_client.get_user()

    securities_account = authenticated_client.get_securities_account(user.securities_account.id)

    assert securities_account.id == user.securities_account.id
    assert securities_account.private_account

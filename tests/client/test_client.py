"""
Integration tests for the Alpha Trader Client.

These tests require a live connection to the Alpha Trader API.
Set the following environment variables before running:
    - BASE_URL: The base URL of the Alpha Trader API
    - USERNAME: Username for authentication
    - PASSWORD: Password for authentication
    - PARTNER_ID: Partner ID for authentication

Usage:
    pytest tests/client/test_client.py -v
"""

import pytest


class TestClientAuthentication:
    """Tests for client authentication."""

    def test_login_sets_authenticated_flag(self, api_credentials):
        """Test that login sets the authenticated flag."""
        from alpha_trader.client import Client

        fresh_client = Client(
            base_url=api_credentials["base_url"],
            username=api_credentials["username"],
            password=api_credentials["password"],
            partner_id=api_credentials["partner_id"],
        )

        assert fresh_client.authenticated is False

        fresh_client.login()

        assert fresh_client.authenticated is True

    def test_login_returns_token(self, api_credentials):
        """Test that login returns a valid token."""
        from alpha_trader.client import Client

        fresh_client = Client(
            base_url=api_credentials["base_url"],
            username=api_credentials["username"],
            password=api_credentials["password"],
            partner_id=api_credentials["partner_id"],
        )

        token = fresh_client.login()

        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0
        assert fresh_client.token == token


class TestClientUserOperations:
    """Tests for user-related client operations."""

    def test_get_user_returns_valid_user(self, authenticated_client):
        """Test that get_user returns a valid user object."""
        user = authenticated_client.get_user()

        assert user is not None
        assert user.id is not None
        assert user.username is not None
        assert user.my_user is True

    def test_get_user_includes_email_for_own_user(self, authenticated_client):
        """Test that own user includes email address."""
        user = authenticated_client.get_user()

        assert user.email is not None
        assert "@" in user.email

    def test_get_user_includes_jwt_token(self, authenticated_client):
        """Test that own user includes JWT token."""
        user = authenticated_client.get_user()

        assert user.jwt_token is not None


class TestClientMinerOperations:
    """Tests for miner-related client operations."""

    def test_get_miner_returns_valid_miner(self, authenticated_client):
        """Test that get_miner returns a valid miner object."""
        miner = authenticated_client.get_miner()

        assert miner is not None
        assert miner.id is not None

    def test_miner_has_expected_attributes(self, miner):
        """Test that miner has expected attributes."""
        assert hasattr(miner, "coins_per_hour")
        assert hasattr(miner, "transferable_coins")
        assert hasattr(miner, "storage")
        assert hasattr(miner, "maximum_capacity")


class TestClientListingOperations:
    """Tests for listing-related client operations."""

    def test_get_listing_for_alphacoin(self, authenticated_client):
        """Test getting listing for AlphaCoins."""
        listing = authenticated_client.get_listing("ACALPHCOIN")

        assert listing is not None
        assert listing.name == "AlphaCoins"
        assert listing.security_identifier == "ACALPHCOIN"
        assert listing.type == "COIN"

    def test_get_listing_has_expected_attributes(self, authenticated_client):
        """Test that listing has expected attributes."""
        listing = authenticated_client.get_listing("ACALPHCOIN")

        assert hasattr(listing, "name")
        assert hasattr(listing, "security_identifier")
        assert hasattr(listing, "type")
        assert hasattr(listing, "start_date")
        assert hasattr(listing, "end_date")


class TestClientPriceSpreadOperations:
    """Tests for price spread client operations."""

    def test_get_price_spread_for_alphacoin(self, authenticated_client):
        """Test getting price spread for AlphaCoins."""
        price_spread = authenticated_client.get_price_spread("ACALPHCOIN")

        assert price_spread is not None
        assert price_spread.security_identifier == "ACALPHCOIN"

    def test_price_spread_includes_listing(self, authenticated_client):
        """Test that price spread includes listing information."""
        price_spread = authenticated_client.get_price_spread("ACALPHCOIN")

        assert price_spread.listing is not None
        assert price_spread.listing.security_identifier == "ACALPHCOIN"

    def test_price_spread_has_last_price(self, authenticated_client):
        """Test that price spread has last price."""
        price_spread = authenticated_client.get_price_spread("ACALPHCOIN")

        assert price_spread.last_price is not None


class TestClientSecuritiesAccountOperations:
    """Tests for securities account client operations."""

    def test_get_securities_account(self, authenticated_client, user):
        """Test getting a securities account by ID."""
        securities_account = authenticated_client.get_securities_account(
            user.securities_account.id
        )

        assert securities_account is not None
        assert securities_account.id == user.securities_account.id

    def test_securities_account_is_private(self, authenticated_client, user):
        """Test that user's securities account is marked as private."""
        securities_account = authenticated_client.get_securities_account(
            user.securities_account.id
        )

        assert securities_account.private_account is True

    def test_securities_account_has_clearing_account(self, authenticated_client, user):
        """Test that securities account has a clearing account ID."""
        securities_account = authenticated_client.get_securities_account(
            user.securities_account.id
        )

        assert securities_account.clearing_account_id is not None

"""
Integration tests for newly implemented API features.

These tests require environment variables:
- BASE_URL: API base URL
- USERNAME: User's username
- PASSWORD: User's password
- PARTNER_ID: Partner ID for authentication

Tests marked with @pytest.mark.integration require a live API connection.
"""

import os
import pytest
from alpha_trader.client import Client


def get_authenticated_client():
    """Helper to create and authenticate a client."""
    client = Client(
        base_url=os.getenv("BASE_URL"),
        username=os.getenv("USERNAME"),
        password=os.getenv("PASSWORD"),
        partner_id=os.getenv("PARTNER_ID"),
    )
    client.login()
    return client


@pytest.fixture(scope="module")
def client():
    """Fixture that provides an authenticated client for all tests."""
    return get_authenticated_client()


class TestTradeStatsIntegration:
    """Integration tests for trade statistics."""

    def test_get_trade_summary(self, client):
        """Test retrieving trade summary."""
        summary = client.trade_stats.get_summary()

        assert summary is not None
        assert hasattr(summary, "total_trades")
        assert hasattr(summary, "win_rate")
        assert hasattr(summary, "net_profit_loss")
        assert summary.total_trades >= 0
        assert 0 <= summary.win_rate <= 1

    def test_get_winning_trades(self, client):
        """Test retrieving winning trades."""
        trades = client.trade_stats.get_winning_trades(page=0, size=5)

        assert isinstance(trades, list)
        for trade in trades:
            assert trade.profit_loss >= 0

    def test_get_losing_trades(self, client):
        """Test retrieving losing trades."""
        trades = client.trade_stats.get_losing_trades(page=0, size=5)

        assert isinstance(trades, list)
        for trade in trades:
            assert trade.profit_loss <= 0


class TestHighscoreIntegration:
    """Integration tests for highscores."""

    def test_get_user_highscores(self, client):
        """Test retrieving user highscores."""
        highscores = client.get_user_highscores(page=0, size=10)

        assert isinstance(highscores, list)
        assert len(highscores) <= 10
        for entry in highscores:
            assert hasattr(entry, "username")
            assert hasattr(entry, "value")
            assert entry.value >= 0

    def test_get_company_highscores(self, client):
        """Test retrieving company highscores."""
        highscores = client.get_company_highscores(page=0, size=10)

        assert isinstance(highscores, list)
        for entry in highscores:
            assert hasattr(entry, "company_name")
            assert hasattr(entry, "value")

    def test_get_alliance_highscores(self, client):
        """Test retrieving alliance highscores."""
        highscores = client.get_alliance_highscores(page=0, size=10)

        assert isinstance(highscores, list)
        for entry in highscores:
            assert hasattr(entry, "alliance_name")


class TestIndexIntegration:
    """Integration tests for market indexes."""

    def test_get_indexes(self, client):
        """Test retrieving list of indexes."""
        indexes = client.get_indexes(page=0, size=10)

        assert isinstance(indexes, list)
        for index in indexes:
            assert hasattr(index, "name")
            assert hasattr(index, "security_identifier")
            assert hasattr(index, "members_count")

    def test_get_index_details(self, client):
        """Test retrieving detailed index information."""
        # First get list of indexes
        indexes = client.get_indexes(page=0, size=1)

        if len(indexes) > 0:
            # Get detailed info for first index
            index = client.get_index(indexes[0].security_identifier)

            assert hasattr(index, "name")
            assert hasattr(index, "members")
            assert hasattr(index, "base_value")
            assert isinstance(index.members, list)


class TestWarrantIntegration:
    """Integration tests for warrants."""

    def test_get_warrants(self, client):
        """Test retrieving list of warrants."""
        warrants = client.get_warrants(page=0, size=10)

        assert isinstance(warrants, list)
        for warrant in warrants:
            assert hasattr(warrant, "type")
            assert warrant.type in ("CALL", "PUT")
            assert hasattr(warrant, "security_identifier")
            assert hasattr(warrant, "underlying_security_identifier")


class TestHistoricalDataIntegration:
    """Integration tests for historical data."""

    def test_get_listing_history(self, client):
        """Test retrieving listing history for AlphaCoins (always exists)."""
        history = client.get_listing_history("ACALPHCOIN", page=0, size=10)

        assert isinstance(history, list)
        for data_point in history:
            assert hasattr(data_point, "date")
            assert hasattr(data_point, "open_price")
            assert hasattr(data_point, "close_price")
            assert hasattr(data_point, "high_price")
            assert hasattr(data_point, "low_price")


class TestNotificationIntegration:
    """Integration tests for notifications."""

    def test_get_notifications(self, client):
        """Test retrieving notifications."""
        notifications = client.get_notifications(page=0, size=10)

        assert isinstance(notifications, list)
        for notification in notifications:
            assert hasattr(notification, "id")
            assert hasattr(notification, "subject")
            assert hasattr(notification, "read_by_receiver")

    def test_get_unread_count(self, client):
        """Test getting unread notification count."""
        count = client.get_unread_notification_count()

        assert isinstance(count, int)
        assert count >= 0


class TestSystemBondIntegration:
    """Integration tests for system bonds and interest rates."""

    def test_get_main_interest_rate(self, client):
        """Test retrieving main interest rate."""
        rate = client.get_main_interest_rate()

        assert isinstance(rate, float)
        # Interest rate should be reasonable (0% to 100%)
        assert 0 <= rate <= 1

    def test_get_average_bond_interest_rate(self, client):
        """Test retrieving average bond interest rate."""
        rate = client.get_average_bond_interest_rate()

        assert isinstance(rate, float)
        assert rate >= 0

    def test_get_system_bonds(self, client):
        """Test retrieving system bonds."""
        bonds = client.get_system_bonds()

        assert isinstance(bonds, list)
        for bond in bonds:
            assert hasattr(bond, "name")
            assert hasattr(bond, "interest_rate")
            assert hasattr(bond, "face_value")


class TestOrderLogIntegration:
    """Integration tests for order logs."""

    def test_get_order_logs(self, client):
        """Test retrieving order logs."""
        logs = client.get_order_logs(page=0, size=10)

        assert isinstance(logs, list)
        for log in logs:
            assert hasattr(log, "id")
            assert hasattr(log, "security_identifier")
            assert hasattr(log, "price")
            assert hasattr(log, "number_of_shares")

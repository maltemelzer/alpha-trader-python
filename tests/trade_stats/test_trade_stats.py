import pytest
from unittest.mock import Mock, patch
from alpha_trader.trade_stats import TradeStats, TradeSummary, Trade


class TestTradeSummary:
    """Unit tests for TradeSummary model."""

    def test_initialize_from_api_response(self):
        """Test TradeSummary initialization from API response."""
        api_response = {
            "breakEvenTrades": 5,
            "losingTrades": 10,
            "netProfitLoss": 1500.50,
            "totalLoss": 500.25,
            "totalProfit": 2000.75,
            "totalTrades": 25,
            "winRate": 0.4,
            "winningTrades": 10,
        }

        summary = TradeSummary.initialize_from_api_response(api_response)

        assert summary.break_even_trades == 5
        assert summary.losing_trades == 10
        assert summary.net_profit_loss == 1500.50
        assert summary.total_loss == 500.25
        assert summary.total_profit == 2000.75
        assert summary.total_trades == 25
        assert summary.win_rate == 0.4
        assert summary.winning_trades == 10

    def test_initialize_from_empty_response(self):
        """Test TradeSummary with missing fields uses defaults."""
        api_response = {}

        summary = TradeSummary.initialize_from_api_response(api_response)

        assert summary.break_even_trades == 0
        assert summary.losing_trades == 0
        assert summary.net_profit_loss == 0.0
        assert summary.total_trades == 0
        assert summary.win_rate == 0.0

    def test_str_representation(self):
        """Test string representation of TradeSummary."""
        summary = TradeSummary(
            break_even_trades=0,
            losing_trades=5,
            net_profit_loss=1000.0,
            total_loss=500.0,
            total_profit=1500.0,
            total_trades=20,
            win_rate=0.75,
            winning_trades=15,
        )

        str_repr = str(summary)
        assert "total_trades=20" in str_repr
        assert "win_rate=75.00%" in str_repr
        assert "net_profit_loss=1000.00" in str_repr


class TestTrade:
    """Unit tests for Trade model."""

    def test_initialize_from_api_response(self):
        """Test Trade initialization from API response."""
        api_response = {
            "tradeId": "trade-123",
            "securityIdentifier": "ASIN456",
            "listingName": "Test Company",
            "numberOfShares": 100,
            "averageBuyingPrice": 50.0,
            "sellPrice": 60.0,
            "profitLoss": 1000.0,
            "profitLossPercentage": 0.20,
            "dateCreated": "2024-01-15T10:30:00Z",
        }

        trade = Trade.initialize_from_api_response(api_response)

        assert trade.trade_id == "trade-123"
        assert trade.security_identifier == "ASIN456"
        assert trade.listing_name == "Test Company"
        assert trade.number_of_shares == 100
        assert trade.average_buying_price == 50.0
        assert trade.sell_price == 60.0
        assert trade.profit_loss == 1000.0
        assert trade.profit_loss_percentage == 0.20
        assert trade.date_created == "2024-01-15T10:30:00Z"

    def test_str_representation(self):
        """Test string representation of Trade."""
        trade = Trade(
            trade_id="123",
            security_identifier="ASIN",
            listing_name="Test Co",
            number_of_shares=100,
            average_buying_price=50.0,
            sell_price=60.0,
            profit_loss=1000.0,
            profit_loss_percentage=0.20,
            date_created="2024-01-15",
        )

        str_repr = str(trade)
        assert "Test Co" in str_repr
        assert "shares=100" in str_repr
        assert "1000.00" in str_repr


class TestTradeStats:
    """Unit tests for TradeStats accessor."""

    @pytest.fixture
    def mock_client(self):
        """Create a mock client for testing."""
        client = Mock()
        client.authenticated = True
        return client

    def test_get_summary(self, mock_client):
        """Test get_summary method."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "totalTrades": 10,
            "winningTrades": 6,
            "losingTrades": 4,
            "winRate": 0.6,
            "netProfitLoss": 500.0,
            "totalProfit": 800.0,
            "totalLoss": 300.0,
            "breakEvenTrades": 0,
        }
        mock_client.request.return_value = mock_response

        trade_stats = TradeStats(mock_client)
        summary = trade_stats.get_summary()

        mock_client.request.assert_called_once_with(
            "GET", "api/v2/trades/stats/summary", params={}
        )
        assert summary.total_trades == 10
        assert summary.win_rate == 0.6

    def test_get_summary_with_filters(self, mock_client):
        """Test get_summary with filter parameters."""
        mock_response = Mock()
        mock_response.json.return_value = {"totalTrades": 5}
        mock_client.request.return_value = mock_response

        trade_stats = TradeStats(mock_client)
        trade_stats.get_summary(
            securities_account_id="acc-123",
            security_identifier="ASIN456",
            start_date="2024-01-01",
            end_date="2024-12-31",
        )

        mock_client.request.assert_called_once()
        call_args = mock_client.request.call_args
        params = call_args[1]["params"]
        assert params["securitiesAccountId"] == "acc-123"
        assert params["securityIdentifier"] == "ASIN456"
        assert params["startDate"] == "2024-01-01"
        assert params["endDate"] == "2024-12-31"

    def test_get_best_trade(self, mock_client):
        """Test get_best_trade method."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "tradeId": "best-trade",
            "profitLoss": 5000.0,
            "listingName": "Winner Stock",
        }
        mock_client.request.return_value = mock_response

        trade_stats = TradeStats(mock_client)
        best_trade = trade_stats.get_best_trade()

        assert best_trade is not None
        assert best_trade.trade_id == "best-trade"
        assert best_trade.profit_loss == 5000.0

    def test_get_best_trade_returns_none_when_no_trades(self, mock_client):
        """Test get_best_trade returns None when no trades exist."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = None
        mock_client.request.return_value = mock_response

        trade_stats = TradeStats(mock_client)
        best_trade = trade_stats.get_best_trade()

        assert best_trade is None

    def test_get_worst_trade(self, mock_client):
        """Test get_worst_trade method."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "tradeId": "worst-trade",
            "profitLoss": -2000.0,
            "listingName": "Loser Stock",
        }
        mock_client.request.return_value = mock_response

        trade_stats = TradeStats(mock_client)
        worst_trade = trade_stats.get_worst_trade()

        assert worst_trade is not None
        assert worst_trade.profit_loss == -2000.0

    def test_get_winning_trades(self, mock_client):
        """Test get_winning_trades method."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "content": [
                {"tradeId": "win-1", "profitLoss": 100.0},
                {"tradeId": "win-2", "profitLoss": 200.0},
            ]
        }
        mock_client.request.return_value = mock_response

        trade_stats = TradeStats(mock_client)
        trades = trade_stats.get_winning_trades(page=0, size=10)

        assert len(trades) == 2
        assert trades[0].trade_id == "win-1"
        assert trades[1].trade_id == "win-2"

    def test_get_losing_trades(self, mock_client):
        """Test get_losing_trades method."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "content": [
                {"tradeId": "loss-1", "profitLoss": -50.0},
                {"tradeId": "loss-2", "profitLoss": -75.0},
            ]
        }
        mock_client.request.return_value = mock_response

        trade_stats = TradeStats(mock_client)
        trades = trade_stats.get_losing_trades(page=0, size=10)

        assert len(trades) == 2
        assert trades[0].profit_loss == -50.0

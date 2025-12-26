import pytest
from unittest.mock import Mock
from alpha_trader.historical_data import (
    HistorizedCompanyData,
    HistorizedListingData,
    get_company_history,
    get_listing_history,
)


class TestHistorizedCompanyData:
    """Unit tests for HistorizedCompanyData model."""

    def test_initialize_from_api_response(self):
        """Test HistorizedCompanyData initialization from API response."""
        api_response = {
            "id": "hcd-123",
            "date": "2024-01-15",
            "bookValue": 1000000.0,
            "bookValuePerShare": 100.0,
            "cash": 500000.0,
            "cashFlow": 50000.0,
            "netCash": 400000.0,
            "netCashPerShare": 40.0,
            "fairValuePerShare": 110.0,
            "freeFloatInPercent": 0.65,
            "bondsVolume": 200000.0,
            "centralBankReserves": 100000.0,
            "reposVolume": 50000.0,
            "systemReposVolume": 25000.0,
            "version": 1,
        }

        data = HistorizedCompanyData.initialize_from_api_response(api_response)

        assert data.id == "hcd-123"
        assert data.date == "2024-01-15"
        assert data.book_value == 1000000.0
        assert data.book_value_per_share == 100.0
        assert data.cash == 500000.0
        assert data.cash_flow == 50000.0
        assert data.net_cash == 400000.0
        assert data.net_cash_per_share == 40.0
        assert data.fair_value_per_share == 110.0
        assert data.free_float_in_percent == 0.65
        assert data.bonds_volume == 200000.0
        assert data.central_bank_reserves == 100000.0
        assert data.repos_volume == 50000.0
        assert data.system_repos_volume == 25000.0
        assert data.version == 1

    def test_initialize_with_defaults(self):
        """Test HistorizedCompanyData with missing fields uses defaults."""
        api_response = {"id": "hcd-456", "date": "2024-01-15"}

        data = HistorizedCompanyData.initialize_from_api_response(api_response)

        assert data.id == "hcd-456"
        assert data.book_value == 0.0
        assert data.cash == 0.0

    def test_str_representation(self):
        """Test string representation of HistorizedCompanyData."""
        data = HistorizedCompanyData(
            id="123",
            date="2024-01-15",
            book_value=1000000.0,
            book_value_per_share=100.0,
            cash=500000.0,
            cash_flow=50000.0,
            net_cash=400000.0,
            net_cash_per_share=40.0,
            fair_value_per_share=110.0,
            free_float_in_percent=0.65,
            bonds_volume=0.0,
            central_bank_reserves=0.0,
            repos_volume=0.0,
            system_repos_volume=0.0,
            version=1,
        )

        str_repr = str(data)
        assert "2024-01-15" in str_repr
        assert "1000000.00" in str_repr


class TestHistorizedListingData:
    """Unit tests for HistorizedListingData model."""

    def test_initialize_from_api_response(self):
        """Test HistorizedListingData initialization from API response."""
        api_response = {
            "id": "hld-123",
            "date": "2024-01-15",
            "openPrice": 100.0,
            "highPrice": 110.0,
            "lowPrice": 95.0,
            "closePrice": 108.0,
            "askPrice": 108.5,
            "bidPrice": 107.5,
            "outstandingShares": 10000,
            "sharesInBuys": 500,
            "sharesInSells": 300,
            "tradeVolume": 50000.0,
            "version": 1,
        }

        data = HistorizedListingData.initialize_from_api_response(api_response)

        assert data.id == "hld-123"
        assert data.date == "2024-01-15"
        assert data.open_price == 100.0
        assert data.high_price == 110.0
        assert data.low_price == 95.0
        assert data.close_price == 108.0
        assert data.ask_price == 108.5
        assert data.bid_price == 107.5
        assert data.outstanding_shares == 10000
        assert data.shares_in_buys == 500
        assert data.shares_in_sells == 300
        assert data.trade_volume == 50000.0
        assert data.version == 1

    def test_initialize_with_defaults(self):
        """Test HistorizedListingData with missing fields uses defaults."""
        api_response = {"id": "hld-456", "date": "2024-01-15"}

        data = HistorizedListingData.initialize_from_api_response(api_response)

        assert data.id == "hld-456"
        assert data.open_price == 0.0
        assert data.close_price == 0.0
        assert data.outstanding_shares == 0

    def test_str_representation(self):
        """Test string representation of HistorizedListingData (OHLC format)."""
        data = HistorizedListingData(
            id="123",
            date="2024-01-15",
            open_price=100.0,
            high_price=110.0,
            low_price=95.0,
            close_price=108.0,
            ask_price=108.5,
            bid_price=107.5,
            outstanding_shares=10000,
            shares_in_buys=500,
            shares_in_sells=300,
            trade_volume=50000.0,
            version=1,
        )

        str_repr = str(data)
        assert "2024-01-15" in str_repr
        assert "O=100.00" in str_repr
        assert "H=110.00" in str_repr
        assert "L=95.00" in str_repr
        assert "C=108.00" in str_repr


class TestGetCompanyHistory:
    """Unit tests for get_company_history function."""

    @pytest.fixture
    def mock_client(self):
        """Create a mock client for testing."""
        client = Mock()
        client.authenticated = True
        return client

    def test_get_company_history(self, mock_client):
        """Test get_company_history function."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "content": [
                {"id": "hcd-1", "date": "2024-01-15", "bookValue": 1000000},
                {"id": "hcd-2", "date": "2024-01-14", "bookValue": 990000},
            ]
        }
        mock_client.request.return_value = mock_response

        history = get_company_history(mock_client, "ASIN123")

        mock_client.request.assert_called_once()
        call_args = mock_client.request.call_args
        assert "ASIN123" in call_args[0][1]
        assert len(history) == 2
        assert history[0].book_value == 1000000

    def test_get_company_history_with_pagination(self, mock_client):
        """Test get_company_history with pagination."""
        mock_response = Mock()
        mock_response.json.return_value = {"content": []}
        mock_client.request.return_value = mock_response

        get_company_history(mock_client, "ASIN123", page=1, size=50, sort="date,desc")

        call_args = mock_client.request.call_args
        params = call_args[1]["params"]
        assert params["page"] == 1
        assert params["size"] == 50
        assert params["sort"] == "date,desc"


class TestGetListingHistory:
    """Unit tests for get_listing_history function."""

    @pytest.fixture
    def mock_client(self):
        """Create a mock client for testing."""
        client = Mock()
        client.authenticated = True
        return client

    def test_get_listing_history(self, mock_client):
        """Test get_listing_history function."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "content": [
                {
                    "id": "hld-1",
                    "date": "2024-01-15",
                    "openPrice": 100.0,
                    "closePrice": 105.0,
                },
                {
                    "id": "hld-2",
                    "date": "2024-01-14",
                    "openPrice": 98.0,
                    "closePrice": 100.0,
                },
            ]
        }
        mock_client.request.return_value = mock_response

        history = get_listing_history(mock_client, "ASIN123")

        mock_client.request.assert_called_once()
        call_args = mock_client.request.call_args
        assert "ASIN123" in call_args[0][1]
        assert len(history) == 2
        assert history[0].open_price == 100.0
        assert history[0].close_price == 105.0

    def test_get_listing_history_with_pagination(self, mock_client):
        """Test get_listing_history with pagination."""
        mock_response = Mock()
        mock_response.json.return_value = {"content": []}
        mock_client.request.return_value = mock_response

        get_listing_history(mock_client, "ASIN123", page=2, size=200, sort="date,asc")

        call_args = mock_client.request.call_args
        params = call_args[1]["params"]
        assert params["page"] == 2
        assert params["size"] == 200
        assert params["sort"] == "date,asc"

    def test_get_listing_history_empty(self, mock_client):
        """Test get_listing_history with empty result."""
        mock_response = Mock()
        mock_response.json.return_value = {"content": []}
        mock_client.request.return_value = mock_response

        history = get_listing_history(mock_client, "NONEXISTENT")

        assert history == []

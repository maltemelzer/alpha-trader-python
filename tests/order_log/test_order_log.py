import pytest
from unittest.mock import Mock
from alpha_trader.order_log import OrderLogEntry, get_order_logs, get_order_logs_by_security


class TestOrderLogEntry:
    """Unit tests for OrderLogEntry model."""

    def test_initialize_from_api_response(self):
        """Test OrderLogEntry initialization from API response."""
        api_response = {
            "id": "log-123",
            "securityIdentifier": "ASIN456",
            "date": 1704067200000,
            "numberOfShares": 100,
            "price": 50.25,
            "volume": 5025.0,
            "buyerSecuritiesAccount": "buyer-acc-123",
            "buyerSecuritiesAccountName": "Buyer Corp",
            "sellerSecuritiesAccount": "seller-acc-456",
            "sellerSecuritiesAccountName": "Seller Inc",
            "sellerAverageBuyingPrice": 45.0,
            "version": 1,
        }

        entry = OrderLogEntry.initialize_from_api_response(api_response)

        assert entry.id == "log-123"
        assert entry.security_identifier == "ASIN456"
        assert entry.date == 1704067200000
        assert entry.number_of_shares == 100
        assert entry.price == 50.25
        assert entry.volume == 5025.0
        assert entry.buyer_securities_account == "buyer-acc-123"
        assert entry.buyer_securities_account_name == "Buyer Corp"
        assert entry.seller_securities_account == "seller-acc-456"
        assert entry.seller_securities_account_name == "Seller Inc"
        assert entry.seller_average_buying_price == 45.0
        assert entry.version == 1

    def test_initialize_with_missing_fields(self):
        """Test OrderLogEntry with missing fields uses defaults."""
        api_response = {"id": "log-456"}

        entry = OrderLogEntry.initialize_from_api_response(api_response)

        assert entry.id == "log-456"
        assert entry.security_identifier == ""
        assert entry.number_of_shares == 0
        assert entry.price == 0.0

    def test_str_representation(self):
        """Test string representation of OrderLogEntry."""
        entry = OrderLogEntry(
            id="123",
            security_identifier="TEST",
            date=0,
            number_of_shares=50,
            price=100.0,
            volume=5000.0,
            buyer_securities_account="buyer",
            buyer_securities_account_name="Buyer",
            seller_securities_account="seller",
            seller_securities_account_name="Seller",
            seller_average_buying_price=90.0,
            version=1,
        )

        str_repr = str(entry)
        assert "TEST" in str_repr
        assert "shares=50" in str_repr
        assert "price=100.00" in str_repr


class TestGetOrderLogs:
    """Unit tests for get_order_logs function."""

    @pytest.fixture
    def mock_client(self):
        """Create a mock client for testing."""
        client = Mock()
        client.authenticated = True
        return client

    def test_get_order_logs(self, mock_client):
        """Test get_order_logs function."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "content": [
                {"id": "log-1", "numberOfShares": 100},
                {"id": "log-2", "numberOfShares": 200},
            ]
        }
        mock_client.request.return_value = mock_response

        logs = get_order_logs(mock_client, page=0, size=20)

        mock_client.request.assert_called_once()
        assert len(logs) == 2
        assert logs[0].id == "log-1"
        assert logs[1].number_of_shares == 200

    def test_get_order_logs_with_filters(self, mock_client):
        """Test get_order_logs with filter parameters."""
        mock_response = Mock()
        mock_response.json.return_value = {"content": []}
        mock_client.request.return_value = mock_response

        get_order_logs(
            mock_client,
            securities_account_id="acc-123",
            search="test",
            page=1,
            size=50,
            sort="date,desc",
        )

        call_args = mock_client.request.call_args
        params = call_args[1]["params"]
        assert params["securitiesAccountId"] == "acc-123"
        assert params["search"] == "test"
        assert params["page"] == 1
        assert params["size"] == 50
        assert params["sort"] == "date,desc"

    def test_get_order_logs_empty_response(self, mock_client):
        """Test get_order_logs with empty response."""
        mock_response = Mock()
        mock_response.json.return_value = {"content": []}
        mock_client.request.return_value = mock_response

        logs = get_order_logs(mock_client)

        assert logs == []


class TestGetOrderLogsBySecurity:
    """Unit tests for get_order_logs_by_security function."""

    @pytest.fixture
    def mock_client(self):
        """Create a mock client for testing."""
        client = Mock()
        client.authenticated = True
        return client

    def test_get_order_logs_by_security(self, mock_client):
        """Test get_order_logs_by_security function."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "content": [
                {"id": "log-1", "securityIdentifier": "ASIN123"},
            ]
        }
        mock_client.request.return_value = mock_response

        logs = get_order_logs_by_security(mock_client, "ASIN123")

        mock_client.request.assert_called_once()
        call_args = mock_client.request.call_args
        assert "ASIN123" in call_args[0][1]
        assert len(logs) == 1

    def test_get_order_logs_by_security_with_pagination(self, mock_client):
        """Test get_order_logs_by_security with pagination."""
        mock_response = Mock()
        mock_response.json.return_value = {"content": []}
        mock_client.request.return_value = mock_response

        get_order_logs_by_security(
            mock_client, "ASIN123", page=2, size=100, sort="date,asc"
        )

        call_args = mock_client.request.call_args
        params = call_args[1]["params"]
        assert params["page"] == 2
        assert params["size"] == 100
        assert params["sort"] == "date,asc"

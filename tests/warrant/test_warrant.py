import pytest
from unittest.mock import Mock
from alpha_trader.warrant import (
    Warrant,
    WarrantType,
    get_warrants,
    get_warrant,
)


class TestWarrantType:
    """Unit tests for WarrantType enum."""

    def test_warrant_types_exist(self):
        """Test that all expected warrant types exist."""
        assert WarrantType.CALL == "CALL"
        assert WarrantType.PUT == "PUT"


class TestWarrant:
    """Unit tests for Warrant model."""

    def test_initialize_from_api_response(self):
        """Test Warrant initialization from API response."""
        api_response = {
            "id": "warrant-123",
            "type": "CALL",
            "ratio": 1.5,
            "subscriptionPeriodDate": 1735689600000,
            "underlyingValue": 100.0,
            "underlyingCapValue": 150.0,
            "listing": {
                "securityIdentifier": "WRN123",
            },
            "underlying": {
                "securityIdentifier": "STOCK123",
            },
            "company": {
                "id": "company-456",
                "name": "Issuing Corp",
            },
            "version": 2,
        }

        mock_client = Mock()
        warrant = Warrant.initialize_from_api_response(api_response, mock_client)

        assert warrant.id == "warrant-123"
        assert warrant.type == "CALL"
        assert warrant.ratio == 1.5
        assert warrant.subscription_period_date == 1735689600000
        assert warrant.underlying_value == 100.0
        assert warrant.underlying_cap_value == 150.0
        assert warrant.security_identifier == "WRN123"
        assert warrant.underlying_security_identifier == "STOCK123"
        assert warrant.company_id == "company-456"
        assert warrant.company_name == "Issuing Corp"
        assert warrant.version == 2

    def test_is_call_property(self):
        """Test is_call property."""
        call_warrant = Warrant(
            id="1",
            type="CALL",
            ratio=1.0,
            subscription_period_date=0,
            underlying_value=100.0,
            underlying_cap_value=150.0,
            security_identifier="WRN",
            underlying_security_identifier="STK",
            company_id="c1",
            company_name="Corp",
            version=1,
        )
        put_warrant = Warrant(
            id="2",
            type="PUT",
            ratio=1.0,
            subscription_period_date=0,
            underlying_value=100.0,
            underlying_cap_value=150.0,
            security_identifier="WRN2",
            underlying_security_identifier="STK",
            company_id="c1",
            company_name="Corp",
            version=1,
        )

        assert call_warrant.is_call is True
        assert call_warrant.is_put is False
        assert put_warrant.is_call is False
        assert put_warrant.is_put is True

    def test_str_representation(self):
        """Test string representation of Warrant."""
        warrant = Warrant(
            id="123",
            type="CALL",
            ratio=1.0,
            subscription_period_date=0,
            underlying_value=100.0,
            underlying_cap_value=150.0,
            security_identifier="WRN",
            underlying_security_identifier="STK",
            company_id="c1",
            company_name="Corp",
            version=1,
        )

        str_repr = str(warrant)
        assert "WRN" in str_repr
        assert "CALL" in str_repr
        assert "STK" in str_repr


class TestGetWarrants:
    """Unit tests for get_warrants function."""

    @pytest.fixture
    def mock_client(self):
        """Create a mock client for testing."""
        client = Mock()
        client.authenticated = True
        return client

    def test_get_warrants(self, mock_client):
        """Test get_warrants function."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "content": [
                {
                    "id": "w1",
                    "type": "CALL",
                    "listing": {"securityIdentifier": "WRN1"},
                    "underlying": {"securityIdentifier": "STK1"},
                    "company": {"id": "c1", "name": "Corp1"},
                },
                {
                    "id": "w2",
                    "type": "PUT",
                    "listing": {"securityIdentifier": "WRN2"},
                    "underlying": {"securityIdentifier": "STK1"},
                    "company": {"id": "c2", "name": "Corp2"},
                },
            ]
        }
        mock_client.request.return_value = mock_response

        warrants = get_warrants(mock_client)

        mock_client.request.assert_called_once()
        assert len(warrants) == 2
        assert warrants[0].type == "CALL"
        assert warrants[1].type == "PUT"

    def test_get_warrants_with_underlying_filter(self, mock_client):
        """Test get_warrants with underlying filter."""
        mock_response = Mock()
        mock_response.json.return_value = {"content": []}
        mock_client.request.return_value = mock_response

        get_warrants(mock_client, underlying_asin="STOCK123")

        call_args = mock_client.request.call_args
        params = call_args[1]["params"]
        assert params["underlyingAsin"] == "STOCK123"

    def test_get_warrants_with_pagination(self, mock_client):
        """Test get_warrants with pagination."""
        mock_response = Mock()
        mock_response.json.return_value = {"content": []}
        mock_client.request.return_value = mock_response

        get_warrants(mock_client, page=1, size=50, sort="type,asc")

        call_args = mock_client.request.call_args
        params = call_args[1]["params"]
        assert params["page"] == 1
        assert params["size"] == 50
        assert params["sort"] == "type,asc"


class TestGetWarrant:
    """Unit tests for get_warrant function."""

    @pytest.fixture
    def mock_client(self):
        """Create a mock client for testing."""
        client = Mock()
        client.authenticated = True
        return client

    def test_get_warrant(self, mock_client):
        """Test get_warrant function."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "id": "warrant-123",
            "type": "CALL",
            "ratio": 2.0,
            "listing": {"securityIdentifier": "WRN123"},
            "underlying": {"securityIdentifier": "STK123"},
            "company": {"id": "c1", "name": "Corp"},
        }
        mock_client.request.return_value = mock_response

        warrant = get_warrant(mock_client, "warrant-123")

        mock_client.request.assert_called_once()
        call_args = mock_client.request.call_args
        assert "warrant-123" in call_args[0][1]
        assert warrant.id == "warrant-123"
        assert warrant.ratio == 2.0


class TestWarrantCreate:
    """Unit tests for Warrant.create static method."""

    @pytest.fixture
    def mock_client(self):
        """Create a mock client for testing."""
        client = Mock()
        client.authenticated = True
        return client

    def test_create_warrant(self, mock_client):
        """Test Warrant.create static method."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "id": "new-warrant",
            "type": "CALL",
            "ratio": 1.0,
            "listing": {"securityIdentifier": "NEW_WRN"},
            "underlying": {"securityIdentifier": "UNDER"},
            "company": {"id": "comp", "name": "Corp"},
        }
        mock_client.request.return_value = mock_response

        warrant = Warrant.create(
            client=mock_client,
            company_id="comp",
            underlying_asin="UNDER",
            warrant_type=WarrantType.CALL,
            cash_deposit=10000.0,
        )

        mock_client.request.assert_called_once()
        call_args = mock_client.request.call_args
        params = call_args[1]["params"]
        assert params["companyId"] == "comp"
        assert params["underlyingAsin"] == "UNDER"
        assert params["type"] == "CALL"
        assert params["cashDeposit"] == 10000.0
        assert warrant.id == "new-warrant"

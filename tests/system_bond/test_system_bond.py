import pytest
from unittest.mock import Mock
from alpha_trader.system_bond import (
    SystemBond,
    get_system_bonds,
    get_system_bond,
    get_system_bond_by_security,
    get_main_interest_rate,
    get_average_bond_interest_rate,
)


class TestSystemBond:
    """Unit tests for SystemBond model."""

    def test_initialize_from_api_response(self):
        """Test SystemBond initialization from API response."""
        api_response = {
            "id": "bond-123",
            "name": "Central Bank Bond 2024",
            "faceValue": 100.0,
            "volume": 10000.0,
            "interestRate": 0.05,
            "issueDate": 1704067200000,
            "maturityDate": 1735689600000,
            "listing": {
                "securityIdentifier": "SYS123",
            },
            "repurchaseListing": {
                "securityIdentifier": "REPO123",
            },
            "version": 1,
        }

        mock_client = Mock()
        bond = SystemBond.initialize_from_api_response(api_response, mock_client)

        assert bond.id == "bond-123"
        assert bond.name == "Central Bank Bond 2024"
        assert bond.face_value == 100.0
        assert bond.volume == 10000.0
        assert bond.interest_rate == 0.05
        assert bond.issue_date == 1704067200000
        assert bond.maturity_date == 1735689600000
        assert bond.security_identifier == "SYS123"
        assert bond.repurchase_security_identifier == "REPO123"
        assert bond.version == 1

    def test_initialize_with_defaults(self):
        """Test SystemBond with missing fields uses defaults."""
        api_response = {
            "id": "bond-456",
            "listing": {},
            "repurchaseListing": {},
        }

        mock_client = Mock()
        bond = SystemBond.initialize_from_api_response(api_response, mock_client)

        assert bond.id == "bond-456"
        assert bond.name == ""
        assert bond.face_value == 0.0
        assert bond.volume == 0.0
        assert bond.interest_rate == 0.0

    def test_str_representation(self):
        """Test string representation of SystemBond."""
        bond = SystemBond(
            id="123",
            name="Test Bond",
            face_value=100.0,
            volume=5000.0,
            interest_rate=0.045,
            issue_date=0,
            maturity_date=0,
            security_identifier="SYS",
            repurchase_security_identifier="REPO",
            version=1,
        )

        str_repr = str(bond)
        assert "Test Bond" in str_repr
        assert "volume=5000.00" in str_repr
        assert "4.50%" in str_repr

    def test_issue_system_bond(self):
        """Test SystemBond.issue static method."""
        mock_client = Mock()
        mock_response = Mock()
        mock_response.json.return_value = {
            "id": "new-bond",
            "name": "New System Bond",
            "faceValue": 100.0,
            "volume": 1000.0,
            "interestRate": 0.03,
            "listing": {"securityIdentifier": "NEW123"},
            "repurchaseListing": {"securityIdentifier": "REPO123"},
        }
        mock_client.request.return_value = mock_response

        bond = SystemBond.issue(
            client=mock_client,
            company_id="company-123",
            number_of_bonds=1000,
        )

        mock_client.request.assert_called_once()
        call_args = mock_client.request.call_args
        data = call_args[1]["data"]
        assert data["companyId"] == "company-123"
        assert data["numberOfBonds"] == 1000
        assert bond.id == "new-bond"


class TestGetSystemBonds:
    """Unit tests for get_system_bonds function."""

    @pytest.fixture
    def mock_client(self):
        """Create a mock client for testing."""
        client = Mock()
        client.authenticated = True
        return client

    def test_get_system_bonds(self, mock_client):
        """Test get_system_bonds function."""
        mock_response = Mock()
        mock_response.json.return_value = [
            {
                "id": "b1",
                "name": "Bond 1",
                "faceValue": 100.0,
                "volume": 5000.0,
                "listing": {"securityIdentifier": "SYS1"},
                "repurchaseListing": {"securityIdentifier": "REPO1"},
            },
            {
                "id": "b2",
                "name": "Bond 2",
                "faceValue": 100.0,
                "volume": 3000.0,
                "listing": {"securityIdentifier": "SYS2"},
                "repurchaseListing": {"securityIdentifier": "REPO2"},
            },
        ]
        mock_client.request.return_value = mock_response

        bonds = get_system_bonds(mock_client)

        mock_client.request.assert_called_once()
        assert len(bonds) == 2
        assert bonds[0].name == "Bond 1"
        assert bonds[1].volume == 3000.0

    def test_get_system_bonds_empty(self, mock_client):
        """Test get_system_bonds with empty result."""
        mock_response = Mock()
        mock_response.json.return_value = []
        mock_client.request.return_value = mock_response

        bonds = get_system_bonds(mock_client)

        assert bonds == []


class TestGetSystemBond:
    """Unit tests for get_system_bond function."""

    @pytest.fixture
    def mock_client(self):
        """Create a mock client for testing."""
        client = Mock()
        client.authenticated = True
        return client

    def test_get_system_bond(self, mock_client):
        """Test get_system_bond function."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "id": "bond-123",
            "name": "Specific Bond",
            "listing": {"securityIdentifier": "SYS123"},
            "repurchaseListing": {"securityIdentifier": "REPO123"},
        }
        mock_client.request.return_value = mock_response

        bond = get_system_bond(mock_client, "bond-123")

        mock_client.request.assert_called_once()
        call_args = mock_client.request.call_args
        assert "bond-123" in call_args[0][1]
        assert bond.name == "Specific Bond"


class TestGetSystemBondBySecurity:
    """Unit tests for get_system_bond_by_security function."""

    @pytest.fixture
    def mock_client(self):
        """Create a mock client for testing."""
        client = Mock()
        client.authenticated = True
        return client

    def test_get_system_bond_by_security(self, mock_client):
        """Test get_system_bond_by_security function."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "id": "bond-123",
            "name": "Bond by Security",
            "listing": {"securityIdentifier": "SYS123"},
            "repurchaseListing": {"securityIdentifier": "REPO123"},
        }
        mock_client.request.return_value = mock_response

        bond = get_system_bond_by_security(mock_client, "SYS123")

        mock_client.request.assert_called_once()
        call_args = mock_client.request.call_args
        assert "SYS123" in call_args[0][1]
        assert bond.id == "bond-123"


class TestGetMainInterestRate:
    """Unit tests for get_main_interest_rate function."""

    @pytest.fixture
    def mock_client(self):
        """Create a mock client for testing."""
        client = Mock()
        client.authenticated = True
        return client

    def test_get_main_interest_rate(self, mock_client):
        """Test get_main_interest_rate function."""
        mock_response = Mock()
        mock_response.json.return_value = {"value": 0.025}
        mock_client.request.return_value = mock_response

        rate = get_main_interest_rate(mock_client)

        mock_client.request.assert_called_once()
        call_args = mock_client.request.call_args
        assert call_args[0][1] == "api/maininterestrate/latest/"
        assert rate == 0.025

    def test_get_main_interest_rate_zero(self, mock_client):
        """Test get_main_interest_rate when rate is zero."""
        mock_response = Mock()
        mock_response.json.return_value = {"value": 0.0}
        mock_client.request.return_value = mock_response

        rate = get_main_interest_rate(mock_client)

        assert rate == 0.0


class TestGetAverageBondInterestRate:
    """Unit tests for get_average_bond_interest_rate function."""

    @pytest.fixture
    def mock_client(self):
        """Create a mock client for testing."""
        client = Mock()
        client.authenticated = True
        return client

    def test_get_average_bond_interest_rate(self, mock_client):
        """Test get_average_bond_interest_rate function."""
        mock_response = Mock()
        mock_response.json.return_value = {"value": 0.035}
        mock_client.request.return_value = mock_response

        rate = get_average_bond_interest_rate(mock_client)

        mock_client.request.assert_called_once()
        call_args = mock_client.request.call_args
        assert call_args[0][1] == "api/v2/averagebondinterestrate"
        assert rate == 0.035

    def test_get_average_bond_interest_rate_default(self, mock_client):
        """Test get_average_bond_interest_rate with missing value."""
        mock_response = Mock()
        mock_response.json.return_value = {}
        mock_client.request.return_value = mock_response

        rate = get_average_bond_interest_rate(mock_client)

        assert rate == 0.0

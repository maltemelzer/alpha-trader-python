import pytest
from unittest.mock import Mock
from alpha_trader.highscore import (
    HighscoreType,
    UserHighscoreEntry,
    CompanyHighscoreEntry,
    AllianceHighscoreEntry,
    get_user_highscores,
    get_company_highscores,
    get_alliance_highscores,
    get_best_users,
    get_best_companies,
)


class TestHighscoreType:
    """Unit tests for HighscoreType enum."""

    def test_highscore_types_exist(self):
        """Test that all expected highscore types exist."""
        assert HighscoreType.NETWORTH == "NETWORTH"
        assert HighscoreType.BOOK_VALUE == "BOOK_VALUE"
        assert HighscoreType.CASH == "CASH"
        assert HighscoreType.SHARES == "SHARES"
        assert HighscoreType.DAILY_PROFIT == "DAILY_PROFIT"
        assert HighscoreType.WEEKLY_PROFIT == "WEEKLY_PROFIT"
        assert HighscoreType.MONTHLY_PROFIT == "MONTHLY_PROFIT"


class TestUserHighscoreEntry:
    """Unit tests for UserHighscoreEntry model."""

    def test_initialize_from_api_response(self):
        """Test UserHighscoreEntry initialization from API response."""
        api_response = {
            "user": {
                "id": "user-123",
                "username": "TopTrader",
                "gravatarHash": "abc123",
            },
            "value": 1000000.0,
            "date": "2024-01-15",
            "historyDate": 1704067200000,
            "historyPosition": 5,
            "historyValue": 950000.0,
        }

        entry = UserHighscoreEntry.initialize_from_api_response(api_response)

        assert entry.user_id == "user-123"
        assert entry.username == "TopTrader"
        assert entry.gravatar_hash == "abc123"
        assert entry.value == 1000000.0
        assert entry.date == "2024-01-15"
        assert entry.history_date == 1704067200000
        assert entry.history_position == 5
        assert entry.history_value == 950000.0

    def test_initialize_with_missing_history(self):
        """Test UserHighscoreEntry with missing history fields."""
        api_response = {
            "user": {"id": "user-456", "username": "NewTrader"},
            "value": 50000.0,
            "date": "2024-01-15",
        }

        entry = UserHighscoreEntry.initialize_from_api_response(api_response)

        assert entry.user_id == "user-456"
        assert entry.history_date is None
        assert entry.history_position is None
        assert entry.history_value is None

    def test_str_representation(self):
        """Test string representation of UserHighscoreEntry."""
        entry = UserHighscoreEntry(
            user_id="123",
            username="TestUser",
            gravatar_hash="hash",
            value=100000.0,
            date="2024-01-15",
            history_date=None,
            history_position=None,
            history_value=None,
        )

        str_repr = str(entry)
        assert "TestUser" in str_repr
        assert "100000.00" in str_repr


class TestCompanyHighscoreEntry:
    """Unit tests for CompanyHighscoreEntry model."""

    def test_initialize_from_api_response(self):
        """Test CompanyHighscoreEntry initialization from API response."""
        api_response = {
            "company": {
                "id": "company-123",
                "name": "MegaCorp",
                "securityIdentifier": "MEGA",
            },
            "value": 5000000.0,
            "date": "2024-01-15",
            "historyDate": 1704067200000,
            "historyPosition": 1,
            "historyValue": 4800000.0,
        }

        entry = CompanyHighscoreEntry.initialize_from_api_response(api_response)

        assert entry.company_id == "company-123"
        assert entry.company_name == "MegaCorp"
        assert entry.security_identifier == "MEGA"
        assert entry.value == 5000000.0
        assert entry.history_position == 1


class TestAllianceHighscoreEntry:
    """Unit tests for AllianceHighscoreEntry model."""

    def test_initialize_from_api_response(self):
        """Test AllianceHighscoreEntry initialization from API response."""
        api_response = {
            "alliance": {
                "id": "alliance-123",
                "name": "Super Alliance",
            },
            "value": 10000000.0,
            "date": "2024-01-15",
        }

        entry = AllianceHighscoreEntry.initialize_from_api_response(api_response)

        assert entry.alliance_id == "alliance-123"
        assert entry.alliance_name == "Super Alliance"
        assert entry.value == 10000000.0


class TestGetUserHighscores:
    """Unit tests for get_user_highscores function."""

    @pytest.fixture
    def mock_client(self):
        """Create a mock client for testing."""
        client = Mock()
        client.authenticated = True
        return client

    def test_get_user_highscores(self, mock_client):
        """Test get_user_highscores function."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "content": [
                {"user": {"id": "1", "username": "User1"}, "value": 1000000},
                {"user": {"id": "2", "username": "User2"}, "value": 900000},
            ]
        }
        mock_client.request.return_value = mock_response

        entries = get_user_highscores(mock_client)

        mock_client.request.assert_called_once()
        call_args = mock_client.request.call_args
        assert call_args[0][1] == "api/v2/userhighscores"
        assert len(entries) == 2
        assert entries[0].username == "User1"

    def test_get_user_highscores_with_type(self, mock_client):
        """Test get_user_highscores with specific type."""
        mock_response = Mock()
        mock_response.json.return_value = {"content": []}
        mock_client.request.return_value = mock_response

        get_user_highscores(mock_client, highscore_type=HighscoreType.CASH)

        call_args = mock_client.request.call_args
        params = call_args[1]["params"]
        assert params["highscoreType"] == "CASH"


class TestGetCompanyHighscores:
    """Unit tests for get_company_highscores function."""

    @pytest.fixture
    def mock_client(self):
        """Create a mock client for testing."""
        client = Mock()
        client.authenticated = True
        return client

    def test_get_company_highscores(self, mock_client):
        """Test get_company_highscores function."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "content": [
                {"company": {"id": "c1", "name": "Corp1"}, "value": 5000000},
            ]
        }
        mock_client.request.return_value = mock_response

        entries = get_company_highscores(mock_client)

        assert len(entries) == 1
        assert entries[0].company_name == "Corp1"


class TestGetAllianceHighscores:
    """Unit tests for get_alliance_highscores function."""

    @pytest.fixture
    def mock_client(self):
        """Create a mock client for testing."""
        client = Mock()
        client.authenticated = True
        return client

    def test_get_alliance_highscores(self, mock_client):
        """Test get_alliance_highscores function."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "content": [
                {"alliance": {"id": "a1", "name": "Alliance1"}, "value": 10000000},
            ]
        }
        mock_client.request.return_value = mock_response

        entries = get_alliance_highscores(mock_client)

        assert len(entries) == 1
        assert entries[0].alliance_name == "Alliance1"


class TestGetBestUsersAndCompanies:
    """Unit tests for get_best_users and get_best_companies functions."""

    @pytest.fixture
    def mock_client(self):
        """Create a mock client for testing."""
        client = Mock()
        client.authenticated = True
        return client

    def test_get_best_users(self, mock_client):
        """Test get_best_users function."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "content": [
                {"user": {"id": "1", "username": "BestUser"}, "value": 2000000},
            ]
        }
        mock_client.request.return_value = mock_response

        entries = get_best_users(mock_client)

        call_args = mock_client.request.call_args
        assert call_args[0][1] == "api/v2/bestusers"
        assert len(entries) == 1

    def test_get_best_companies(self, mock_client):
        """Test get_best_companies function."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "content": [
                {"company": {"id": "c1", "name": "BestCorp"}, "value": 8000000},
            ]
        }
        mock_client.request.return_value = mock_response

        entries = get_best_companies(mock_client)

        call_args = mock_client.request.call_args
        assert call_args[0][1] == "api/v2/bestcompanies"
        assert len(entries) == 1

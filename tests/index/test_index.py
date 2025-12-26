import pytest
from unittest.mock import Mock
from alpha_trader.index import (
    IndexMember,
    CompactIndex,
    Index,
    get_indexes,
    get_index,
)


class TestIndexMember:
    """Unit tests for IndexMember model."""

    def test_initialize_from_api_response(self):
        """Test IndexMember initialization from API response."""
        api_response = {
            "securityIdentifier": "ASIN123",
            "name": "Test Company",
            "weight": 0.15,
        }

        member = IndexMember.initialize_from_api_response(api_response)

        assert member.security_identifier == "ASIN123"
        assert member.name == "Test Company"
        assert member.weight == 0.15

    def test_initialize_without_weight(self):
        """Test IndexMember without weight field."""
        api_response = {
            "securityIdentifier": "ASIN456",
            "name": "Another Company",
        }

        member = IndexMember.initialize_from_api_response(api_response)

        assert member.security_identifier == "ASIN456"
        assert member.weight is None


class TestCompactIndex:
    """Unit tests for CompactIndex model."""

    def test_initialize_from_api_response(self):
        """Test CompactIndex initialization from API response."""
        api_response = {
            "id": "index-123",
            "name": "Alpha Index 50",
            "listing": {
                "securityIdentifier": "IDX50",
            },
            "membersCount": 50,
            "owner": {
                "id": "user-456",
                "username": "IndexCreator",
            },
            "version": 3,
        }

        index = CompactIndex.initialize_from_api_response(api_response)

        assert index.id == "index-123"
        assert index.name == "Alpha Index 50"
        assert index.security_identifier == "IDX50"
        assert index.members_count == 50
        assert index.owner_id == "user-456"
        assert index.owner_username == "IndexCreator"
        assert index.version == 3

    def test_str_representation(self):
        """Test string representation of CompactIndex."""
        index = CompactIndex(
            id="123",
            name="Test Index",
            security_identifier="IDX",
            members_count=25,
            owner_id="owner",
            owner_username="Owner",
            version=1,
        )

        str_repr = str(index)
        assert "Test Index" in str_repr
        assert "members=25" in str_repr


class TestIndex:
    """Unit tests for Index model."""

    def test_initialize_from_api_response(self):
        """Test Index initialization from API response."""
        api_response = {
            "name": "Full Index",
            "baseValue": 1000.0,
            "chainingFactor": 1.05,
            "nextChainingDate": 1704067200000,
            "members": [
                {"securityIdentifier": "A1", "name": "Company A", "weight": 0.3},
                {"securityIdentifier": "A2", "name": "Company B", "weight": 0.7},
            ],
            "owner": {
                "id": "owner-123",
                "username": "IndexOwner",
            },
            "listing": {
                "securityIdentifier": "FULLIDX",
            },
        }

        mock_client = Mock()
        index = Index.initialize_from_api_response(api_response, mock_client)

        assert index.name == "Full Index"
        assert index.base_value == 1000.0
        assert index.chaining_factor == 1.05
        assert index.next_chaining_date == 1704067200000
        assert len(index.members) == 2
        assert index.members[0].security_identifier == "A1"
        assert index.members[1].weight == 0.7
        assert index.owner_id == "owner-123"
        assert index.security_identifier == "FULLIDX"

    def test_str_representation(self):
        """Test string representation of Index."""
        index = Index(
            name="Test Index",
            base_value=1000.0,
            chaining_factor=1.0,
            next_chaining_date=0,
            members=[],
            owner_id="owner",
            owner_username="Owner",
            security_identifier="IDX",
        )

        str_repr = str(index)
        assert "Test Index" in str_repr
        assert "base_value=1000.00" in str_repr
        assert "members=0" in str_repr


class TestGetIndexes:
    """Unit tests for get_indexes function."""

    @pytest.fixture
    def mock_client(self):
        """Create a mock client for testing."""
        client = Mock()
        client.authenticated = True
        return client

    def test_get_indexes(self, mock_client):
        """Test get_indexes function."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "content": [
                {
                    "id": "idx-1",
                    "name": "Index 1",
                    "listing": {"securityIdentifier": "IDX1"},
                    "membersCount": 10,
                    "owner": {"id": "o1", "username": "Owner1"},
                    "version": 1,
                },
                {
                    "id": "idx-2",
                    "name": "Index 2",
                    "listing": {"securityIdentifier": "IDX2"},
                    "membersCount": 20,
                    "owner": {"id": "o2", "username": "Owner2"},
                    "version": 1,
                },
            ]
        }
        mock_client.request.return_value = mock_response

        indexes = get_indexes(mock_client)

        mock_client.request.assert_called_once()
        assert len(indexes) == 2
        assert indexes[0].name == "Index 1"
        assert indexes[1].members_count == 20

    def test_get_indexes_with_pagination(self, mock_client):
        """Test get_indexes with pagination parameters."""
        mock_response = Mock()
        mock_response.json.return_value = {"content": []}
        mock_client.request.return_value = mock_response

        get_indexes(mock_client, page=2, size=50, sort="name,asc")

        call_args = mock_client.request.call_args
        params = call_args[1]["params"]
        assert params["page"] == 2
        assert params["size"] == 50
        assert params["sort"] == "name,asc"


class TestGetIndex:
    """Unit tests for get_index function."""

    @pytest.fixture
    def mock_client(self):
        """Create a mock client for testing."""
        client = Mock()
        client.authenticated = True
        return client

    def test_get_index(self, mock_client):
        """Test get_index function."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "name": "Test Index",
            "baseValue": 1000.0,
            "chainingFactor": 1.0,
            "nextChainingDate": 0,
            "members": [
                {"securityIdentifier": "M1", "name": "Member 1"},
            ],
            "owner": {"id": "o1", "username": "Owner"},
            "listing": {"securityIdentifier": "TESTIDX"},
        }
        mock_client.request.return_value = mock_response

        index = get_index(mock_client, "TESTIDX")

        mock_client.request.assert_called_once()
        call_args = mock_client.request.call_args
        assert "TESTIDX" in call_args[0][1]
        assert index.name == "Test Index"
        assert len(index.members) == 1

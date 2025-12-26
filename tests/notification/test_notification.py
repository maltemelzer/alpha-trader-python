import pytest
from unittest.mock import Mock
from alpha_trader.notification import (
    Notification,
    get_notifications,
    get_unread_count,
    mark_all_as_read,
    delete_all_notifications,
)


class TestNotification:
    """Unit tests for Notification model."""

    def test_initialize_from_api_response(self):
        """Test Notification initialization from API response."""
        api_response = {
            "id": "notif-123",
            "subject": {"message": "Trade Executed"},
            "content": {"message": "Your order for 100 shares of STOCK was filled."},
            "date": 1704067200000,
            "readByReceiver": False,
            "receiver": {
                "id": "user-456",
                "username": "Trader",
            },
            "version": 1,
        }

        mock_client = Mock()
        notification = Notification.initialize_from_api_response(api_response, mock_client)

        assert notification.id == "notif-123"
        assert notification.subject == "Trade Executed"
        assert "100 shares" in notification.content
        assert notification.date == 1704067200000
        assert notification.read_by_receiver is False
        assert notification.receiver_id == "user-456"
        assert notification.receiver_username == "Trader"
        assert notification.version == 1

    def test_initialize_with_string_subject_content(self):
        """Test Notification with string subject and content (not MessagePrototype)."""
        api_response = {
            "id": "notif-456",
            "subject": "Simple Subject",
            "content": "Simple Content",
            "date": 1704067200000,
            "readByReceiver": True,
            "receiver": {"id": "u1", "username": "User1"},
            "version": 1,
        }

        mock_client = Mock()
        notification = Notification.initialize_from_api_response(api_response, mock_client)

        assert notification.subject == "Simple Subject"
        assert notification.content == "Simple Content"

    def test_mark_as_read(self):
        """Test mark_as_read method."""
        mock_client = Mock()
        mock_response = Mock()
        mock_response.status_code = 200
        mock_client.request.return_value = mock_response

        notification = Notification(
            id="notif-123",
            subject="Test",
            content="Content",
            date=0,
            read_by_receiver=False,
            receiver_id="u1",
            receiver_username="User1",
            version=1,
            client=mock_client,
        )

        result = notification.mark_as_read()

        assert result is True
        assert notification.read_by_receiver is True
        mock_client.request.assert_called_once()

    def test_mark_as_read_failure(self):
        """Test mark_as_read method when API fails."""
        mock_client = Mock()
        mock_response = Mock()
        mock_response.status_code = 500
        mock_client.request.return_value = mock_response

        notification = Notification(
            id="notif-123",
            subject="Test",
            content="Content",
            date=0,
            read_by_receiver=False,
            receiver_id="u1",
            receiver_username="User1",
            version=1,
            client=mock_client,
        )

        result = notification.mark_as_read()

        assert result is False
        assert notification.read_by_receiver is False

    def test_delete(self):
        """Test delete method."""
        mock_client = Mock()
        mock_response = Mock()
        mock_response.status_code = 200
        mock_client.request.return_value = mock_response

        notification = Notification(
            id="notif-123",
            subject="Test",
            content="Content",
            date=0,
            read_by_receiver=False,
            receiver_id="u1",
            receiver_username="User1",
            version=1,
            client=mock_client,
        )

        result = notification.delete()

        assert result is True
        mock_client.request.assert_called_once()

    def test_str_representation(self):
        """Test string representation of Notification."""
        notification = Notification(
            id="123",
            subject="This is a very long subject that should be truncated",
            content="Content",
            date=0,
            read_by_receiver=False,
            receiver_id="u1",
            receiver_username="User1",
            version=1,
        )

        str_repr = str(notification)
        assert "unread" in str_repr

        notification.read_by_receiver = True
        str_repr = str(notification)
        assert "read" in str_repr


class TestGetNotifications:
    """Unit tests for get_notifications function."""

    @pytest.fixture
    def mock_client(self):
        """Create a mock client for testing."""
        client = Mock()
        client.authenticated = True
        return client

    def test_get_notifications(self, mock_client):
        """Test get_notifications function."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "content": [
                {
                    "id": "n1",
                    "subject": {"message": "Subject 1"},
                    "content": {"message": "Content 1"},
                    "readByReceiver": False,
                    "receiver": {"id": "u1", "username": "User1"},
                },
                {
                    "id": "n2",
                    "subject": {"message": "Subject 2"},
                    "content": {"message": "Content 2"},
                    "readByReceiver": True,
                    "receiver": {"id": "u1", "username": "User1"},
                },
            ]
        }
        mock_client.request.return_value = mock_response

        notifications = get_notifications(mock_client)

        assert len(notifications) == 2
        assert notifications[0].id == "n1"
        assert notifications[0].read_by_receiver is False
        assert notifications[1].read_by_receiver is True

    def test_get_notifications_filter_unread(self, mock_client):
        """Test get_notifications with is_read filter."""
        mock_response = Mock()
        mock_response.json.return_value = {"content": []}
        mock_client.request.return_value = mock_response

        get_notifications(mock_client, is_read=False)

        call_args = mock_client.request.call_args
        params = call_args[1]["params"]
        assert params["isRead"] is False

    def test_get_notifications_with_search(self, mock_client):
        """Test get_notifications with search parameter."""
        mock_response = Mock()
        mock_response.json.return_value = {"content": []}
        mock_client.request.return_value = mock_response

        get_notifications(mock_client, search="trade")

        call_args = mock_client.request.call_args
        params = call_args[1]["params"]
        assert params["search"] == "trade"


class TestGetUnreadCount:
    """Unit tests for get_unread_count function."""

    @pytest.fixture
    def mock_client(self):
        """Create a mock client for testing."""
        client = Mock()
        client.authenticated = True
        return client

    def test_get_unread_count(self, mock_client):
        """Test get_unread_count function."""
        mock_response = Mock()
        mock_response.json.return_value = {"count": 5}
        mock_client.request.return_value = mock_response

        count = get_unread_count(mock_client)

        assert count == 5

    def test_get_unread_count_with_value_key(self, mock_client):
        """Test get_unread_count with 'value' key in response."""
        mock_response = Mock()
        mock_response.json.return_value = {"value": 10}
        mock_client.request.return_value = mock_response

        count = get_unread_count(mock_client)

        assert count == 10


class TestMarkAllAsRead:
    """Unit tests for mark_all_as_read function."""

    @pytest.fixture
    def mock_client(self):
        """Create a mock client for testing."""
        client = Mock()
        client.authenticated = True
        return client

    def test_mark_all_as_read(self, mock_client):
        """Test mark_all_as_read function."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_client.request.return_value = mock_response

        result = mark_all_as_read(mock_client)

        assert result is True
        mock_client.request.assert_called_once()
        call_args = mock_client.request.call_args
        params = call_args[1]["params"]
        assert params["isRead"] is True

    def test_mark_all_as_read_with_search(self, mock_client):
        """Test mark_all_as_read with search filter."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_client.request.return_value = mock_response

        mark_all_as_read(mock_client, search="important")

        call_args = mock_client.request.call_args
        params = call_args[1]["params"]
        assert params["search"] == "important"


class TestDeleteAllNotifications:
    """Unit tests for delete_all_notifications function."""

    @pytest.fixture
    def mock_client(self):
        """Create a mock client for testing."""
        client = Mock()
        client.authenticated = True
        return client

    def test_delete_all_notifications(self, mock_client):
        """Test delete_all_notifications function."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_client.request.return_value = mock_response

        result = delete_all_notifications(mock_client)

        assert result is True
        mock_client.request.assert_called_once()

    def test_delete_all_notifications_failure(self, mock_client):
        """Test delete_all_notifications when API fails."""
        mock_response = Mock()
        mock_response.status_code = 500
        mock_client.request.return_value = mock_response

        result = delete_all_notifications(mock_client)

        assert result is False

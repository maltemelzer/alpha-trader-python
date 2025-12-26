from __future__ import annotations

from pydantic import BaseModel
from typing import Dict, List, Optional, Any, TYPE_CHECKING

if TYPE_CHECKING:
    from alpha_trader.client import Client


class Notification(BaseModel):
    """
    User notification.

    Attributes:
        id: Notification ID
        subject: Notification subject
        content: Notification content
        date: Notification date (timestamp)
        read_by_receiver: Whether the notification has been read
        receiver_id: Receiver user ID
        receiver_username: Receiver username
        version: Entity version
    """
    id: str
    subject: str
    content: str
    date: int
    read_by_receiver: bool
    receiver_id: str
    receiver_username: str
    version: int
    client: Optional[Any] = None

    model_config = {"arbitrary_types_allowed": True}

    @staticmethod
    def initialize_from_api_response(
        api_response: Dict, client: "Client" = None
    ) -> "Notification":
        receiver = api_response.get("receiver", {})
        subject_data = api_response.get("subject", {})
        content_data = api_response.get("content", {})

        # Handle MessagePrototype format
        subject = subject_data.get("message", "") if isinstance(subject_data, dict) else str(subject_data)
        content = content_data.get("message", "") if isinstance(content_data, dict) else str(content_data)

        return Notification(
            id=api_response.get("id", ""),
            subject=subject,
            content=content,
            date=api_response.get("date", 0),
            read_by_receiver=api_response.get("readByReceiver", False),
            receiver_id=receiver.get("id", ""),
            receiver_username=receiver.get("username", ""),
            version=api_response.get("version", 0),
            client=client,
        )

    def mark_as_read(self) -> bool:
        """
        Mark this notification as read.

        Returns:
            True if successful
        """
        params = {"isRead": True, "notificationIds[]": self.id}
        response = self.client.request("PUT", "api/v2/notifications", params=params)
        if response.status_code == 200:
            self.read_by_receiver = True
            return True
        return False

    def delete(self) -> bool:
        """
        Delete this notification.

        Returns:
            True if successful
        """
        params = {"notificationIds[]": self.id}
        response = self.client.request("DELETE", "api/v2/notifications", params=params)
        return response.status_code == 200

    def __str__(self):
        read_status = "read" if self.read_by_receiver else "unread"
        return f"Notification({self.subject[:30]}..., {read_status})"

    def __repr__(self):
        return self.__str__()


def get_notifications(
    client: "Client",
    is_read: Optional[bool] = None,
    search: Optional[str] = None,
    page: int = 0,
    size: int = 20,
    sort: Optional[str] = None,
) -> List[Notification]:
    """
    Get user notifications.

    Args:
        client: API client
        is_read: Filter by read status (None for all)
        search: Optional search string
        page: Page number (0-indexed)
        size: Page size
        sort: Sort order (e.g., "date,desc")

    Returns:
        List of notifications
    """
    params = {"page": page, "size": size}
    if is_read is not None:
        params["isRead"] = is_read
    if search:
        params["search"] = search
    if sort:
        params["sort"] = sort

    response = client.request("GET", "api/v2/notifications", params=params)
    data = response.json()

    # Handle paginated response
    content = data.get("content", data) if isinstance(data, dict) else data
    if isinstance(content, list):
        return [Notification.initialize_from_api_response(item, client) for item in content]
    return []


def get_unread_count(client: "Client") -> int:
    """
    Get count of unread notifications.

    Args:
        client: API client

    Returns:
        Number of unread notifications
    """
    response = client.request("GET", "api/v2/notifications/unread/count")
    data = response.json()
    return data.get("count", data.get("value", 0))


def mark_all_as_read(client: "Client", search: Optional[str] = None) -> bool:
    """
    Mark all notifications as read.

    Args:
        client: API client
        search: Optional search filter to limit which notifications are marked

    Returns:
        True if successful
    """
    params = {"isRead": True}
    if search:
        params["search"] = search

    response = client.request("PUT", "api/v2/notifications", params=params)
    return response.status_code == 200


def delete_all_notifications(client: "Client", search: Optional[str] = None) -> bool:
    """
    Delete all notifications.

    Args:
        client: API client
        search: Optional search filter to limit which notifications are deleted

    Returns:
        True if successful
    """
    params = {}
    if search:
        params["search"] = search

    response = client.request("DELETE", "api/v2/notifications", params=params)
    return response.status_code == 200

from __future__ import annotations

from pydantic import BaseModel
from typing import Dict, List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from alpha_trader.client import Client


class OrderLogEntry(BaseModel):
    """
    Security order log entry representing a completed trade.

    Attributes:
        id: Unique identifier for the log entry
        security_identifier: Security identifier (ASIN)
        date: Timestamp of the trade
        number_of_shares: Number of shares traded
        price: Price per share
        volume: Total trade volume (price * shares)
        buyer_securities_account: Buyer's securities account ID
        buyer_securities_account_name: Buyer's account name
        seller_securities_account: Seller's securities account ID
        seller_securities_account_name: Seller's account name
        seller_average_buying_price: Seller's average buying price
        version: Entity version
    """
    id: str
    security_identifier: str
    date: int
    number_of_shares: int
    price: float
    volume: float
    buyer_securities_account: str
    buyer_securities_account_name: str
    seller_securities_account: str
    seller_securities_account_name: str
    seller_average_buying_price: float
    version: int

    @staticmethod
    def initialize_from_api_response(api_response: Dict) -> "OrderLogEntry":
        return OrderLogEntry(
            id=api_response.get("id", ""),
            security_identifier=api_response.get("securityIdentifier", ""),
            date=api_response.get("date", 0),
            number_of_shares=api_response.get("numberOfShares", 0),
            price=api_response.get("price", 0.0),
            volume=api_response.get("volume", 0.0),
            buyer_securities_account=api_response.get("buyerSecuritiesAccount", ""),
            buyer_securities_account_name=api_response.get("buyerSecuritiesAccountName", ""),
            seller_securities_account=api_response.get("sellerSecuritiesAccount", ""),
            seller_securities_account_name=api_response.get("sellerSecuritiesAccountName", ""),
            seller_average_buying_price=api_response.get("sellerAverageBuyingPrice", 0.0),
            version=api_response.get("version", 0),
        )

    def __str__(self):
        return (
            f"OrderLogEntry({self.security_identifier}, "
            f"shares={self.number_of_shares}, price={self.price:.2f}, "
            f"volume={self.volume:.2f})"
        )

    def __repr__(self):
        return self.__str__()


def get_order_logs(
    client: "Client",
    securities_account_id: Optional[str] = None,
    search: Optional[str] = None,
    page: int = 0,
    size: int = 20,
    sort: Optional[str] = None,
) -> List[OrderLogEntry]:
    """
    Get security order logs (trade history).

    Args:
        client: API client
        securities_account_id: Optional securities account ID to filter by
        search: Optional search string
        page: Page number (0-indexed)
        size: Page size
        sort: Sort order (e.g., "date,desc")

    Returns:
        List of order log entries
    """
    params = {"page": page, "size": size}
    if securities_account_id:
        params["securitiesAccountId"] = securities_account_id
    if search:
        params["search"] = search
    if sort:
        params["sort"] = sort

    response = client.request("GET", "api/v2/securityorderlogs", params=params)
    data = response.json()

    # Handle paginated response
    content = data.get("content", data) if isinstance(data, dict) else data
    if isinstance(content, list):
        return [OrderLogEntry.initialize_from_api_response(item) for item in content]
    return []


def get_order_logs_by_security(
    client: "Client",
    security_identifier: str,
    page: int = 0,
    size: int = 20,
    sort: Optional[str] = None,
) -> List[OrderLogEntry]:
    """
    Get security order logs for a specific security.

    Args:
        client: API client
        security_identifier: Security identifier (ASIN)
        page: Page number (0-indexed)
        size: Page size
        sort: Sort order (e.g., "date,desc")

    Returns:
        List of order log entries for the security
    """
    params = {"page": page, "size": size}
    if sort:
        params["sort"] = sort

    response = client.request(
        "GET", f"api/v2/securityorderlogs/by-asin/{security_identifier}", params=params
    )
    data = response.json()

    # Handle paginated response
    content = data.get("content", data) if isinstance(data, dict) else data
    if isinstance(content, list):
        return [OrderLogEntry.initialize_from_api_response(item) for item in content]
    return []

from __future__ import annotations

from pydantic import BaseModel
from typing import Dict, List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from alpha_trader.client import Client


class HistorizedCompanyData(BaseModel):
    """
    Historical company data point.

    Attributes:
        id: Record ID
        date: Date of the data point
        book_value: Company book value
        book_value_per_share: Book value per share
        cash: Cash position
        cash_flow: Cash flow
        net_cash: Net cash
        net_cash_per_share: Net cash per share
        fair_value_per_share: Fair value per share
        free_float_in_percent: Free float percentage
        bonds_volume: Outstanding bonds volume
        central_bank_reserves: Central bank reserves
        repos_volume: Repo volume
        system_repos_volume: System repo volume
        version: Entity version
    """
    id: str
    date: str
    book_value: float
    book_value_per_share: float
    cash: float
    cash_flow: float
    net_cash: float
    net_cash_per_share: float
    fair_value_per_share: float
    free_float_in_percent: float
    bonds_volume: float
    central_bank_reserves: float
    repos_volume: float
    system_repos_volume: float
    version: int

    @staticmethod
    def initialize_from_api_response(api_response: Dict) -> "HistorizedCompanyData":
        return HistorizedCompanyData(
            id=api_response.get("id", ""),
            date=api_response.get("date", ""),
            book_value=api_response.get("bookValue", 0.0),
            book_value_per_share=api_response.get("bookValuePerShare", 0.0),
            cash=api_response.get("cash", 0.0),
            cash_flow=api_response.get("cashFlow", 0.0),
            net_cash=api_response.get("netCash", 0.0),
            net_cash_per_share=api_response.get("netCashPerShare", 0.0),
            fair_value_per_share=api_response.get("fairValuePerShare", 0.0),
            free_float_in_percent=api_response.get("freeFloatInPercent", 0.0),
            bonds_volume=api_response.get("bondsVolume", 0.0),
            central_bank_reserves=api_response.get("centralBankReserves", 0.0),
            repos_volume=api_response.get("reposVolume", 0.0),
            system_repos_volume=api_response.get("systemReposVolume", 0.0),
            version=api_response.get("version", 0),
        )

    def __str__(self):
        return (
            f"HistorizedCompanyData({self.date}, "
            f"book_value={self.book_value:.2f})"
        )

    def __repr__(self):
        return self.__str__()


class HistorizedListingData(BaseModel):
    """
    Historical listing (price) data point - OHLC data.

    Attributes:
        id: Record ID
        date: Date of the data point
        open_price: Opening price
        high_price: Highest price
        low_price: Lowest price
        close_price: Closing price
        ask_price: Ask price
        bid_price: Bid price
        outstanding_shares: Number of outstanding shares
        shares_in_buys: Shares in buy orders
        shares_in_sells: Shares in sell orders
        trade_volume: Trade volume
        version: Entity version
    """
    id: str
    date: str
    open_price: float
    high_price: float
    low_price: float
    close_price: float
    ask_price: float
    bid_price: float
    outstanding_shares: int
    shares_in_buys: int
    shares_in_sells: int
    trade_volume: float
    version: int

    @staticmethod
    def initialize_from_api_response(api_response: Dict) -> "HistorizedListingData":
        return HistorizedListingData(
            id=api_response.get("id", ""),
            date=api_response.get("date", ""),
            open_price=api_response.get("openPrice", 0.0),
            high_price=api_response.get("highPrice", 0.0),
            low_price=api_response.get("lowPrice", 0.0),
            close_price=api_response.get("closePrice", 0.0),
            ask_price=api_response.get("askPrice", 0.0),
            bid_price=api_response.get("bidPrice", 0.0),
            outstanding_shares=api_response.get("outstandingShares", 0),
            shares_in_buys=api_response.get("sharesInBuys", 0),
            shares_in_sells=api_response.get("sharesInSells", 0),
            trade_volume=api_response.get("tradeVolume", 0.0),
            version=api_response.get("version", 0),
        )

    def __str__(self):
        return (
            f"HistorizedListingData({self.date}, "
            f"O={self.open_price:.2f}, H={self.high_price:.2f}, "
            f"L={self.low_price:.2f}, C={self.close_price:.2f})"
        )

    def __repr__(self):
        return self.__str__()


def get_company_history(
    client: "Client",
    security_identifier: str,
    page: int = 0,
    size: int = 100,
    sort: Optional[str] = None,
) -> List[HistorizedCompanyData]:
    """
    Get historical company data.

    Args:
        client: API client
        security_identifier: Security identifier (ASIN)
        page: Page number (0-indexed)
        size: Page size
        sort: Sort order (e.g., "date,desc")

    Returns:
        List of historical company data points
    """
    params = {"page": page, "size": size}
    if sort:
        params["sort"] = sort

    response = client.request(
        "GET", f"api/v2/historizedcompanydata/{security_identifier}", params=params
    )
    data = response.json()

    # Handle paginated response
    content = data.get("content", data) if isinstance(data, dict) else data
    if isinstance(content, list):
        return [HistorizedCompanyData.initialize_from_api_response(item) for item in content]
    return []


def get_listing_history(
    client: "Client",
    security_identifier: str,
    page: int = 0,
    size: int = 100,
    sort: Optional[str] = None,
) -> List[HistorizedListingData]:
    """
    Get historical listing (price) data - OHLC data.

    Args:
        client: API client
        security_identifier: Security identifier (ASIN)
        page: Page number (0-indexed)
        size: Page size
        sort: Sort order (e.g., "date,desc")

    Returns:
        List of historical listing data points (OHLC)
    """
    params = {"page": page, "size": size}
    if sort:
        params["sort"] = sort

    response = client.request(
        "GET", f"api/v2/historizedlistingdata/{security_identifier}", params=params
    )
    data = response.json()

    # Handle paginated response
    content = data.get("content", data) if isinstance(data, dict) else data
    if isinstance(content, list):
        return [HistorizedListingData.initialize_from_api_response(item) for item in content]
    return []

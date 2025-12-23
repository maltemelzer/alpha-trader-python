from __future__ import annotations

from pydantic import BaseModel
from typing import Dict, List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from alpha_trader.client import Client


class TradeSummary(BaseModel):
    """
    Trade statistics summary.

    Attributes:
        break_even_trades: Number of trades with no profit/loss
        losing_trades: Number of losing trades
        net_profit_loss: Net profit/loss across all trades
        total_loss: Total loss from losing trades
        total_profit: Total profit from winning trades
        total_trades: Total number of trades
        win_rate: Percentage of winning trades
        winning_trades: Number of winning trades
    """
    break_even_trades: int
    losing_trades: int
    net_profit_loss: float
    total_loss: float
    total_profit: float
    total_trades: int
    win_rate: float
    winning_trades: int

    @staticmethod
    def initialize_from_api_response(api_response: Dict) -> "TradeSummary":
        return TradeSummary(
            break_even_trades=api_response.get("breakEvenTrades", 0),
            losing_trades=api_response.get("losingTrades", 0),
            net_profit_loss=api_response.get("netProfitLoss", 0.0),
            total_loss=api_response.get("totalLoss", 0.0),
            total_profit=api_response.get("totalProfit", 0.0),
            total_trades=api_response.get("totalTrades", 0),
            win_rate=api_response.get("winRate", 0.0),
            winning_trades=api_response.get("winningTrades", 0),
        )

    def __str__(self):
        return (
            f"TradeSummary(total_trades={self.total_trades}, "
            f"win_rate={self.win_rate:.2%}, net_profit_loss={self.net_profit_loss:.2f})"
        )

    def __repr__(self):
        return self.__str__()


class Trade(BaseModel):
    """
    Individual trade record.

    Attributes:
        trade_id: Unique identifier for the trade
        security_identifier: Security identifier (ASIN)
        listing_name: Name of the security
        number_of_shares: Number of shares traded
        average_buying_price: Average price paid per share
        sell_price: Price per share when sold
        profit_loss: Absolute profit or loss
        profit_loss_percentage: Percentage profit or loss
        date_created: Date when trade was completed
    """
    trade_id: str
    security_identifier: str
    listing_name: str
    number_of_shares: int
    average_buying_price: float
    sell_price: float
    profit_loss: float
    profit_loss_percentage: float
    date_created: str

    @staticmethod
    def initialize_from_api_response(api_response: Dict) -> "Trade":
        return Trade(
            trade_id=api_response.get("tradeId", ""),
            security_identifier=api_response.get("securityIdentifier", ""),
            listing_name=api_response.get("listingName", ""),
            number_of_shares=api_response.get("numberOfShares", 0),
            average_buying_price=api_response.get("averageBuyingPrice", 0.0),
            sell_price=api_response.get("sellPrice", 0.0),
            profit_loss=api_response.get("profitLoss", 0.0),
            profit_loss_percentage=api_response.get("profitLossPercentage", 0.0),
            date_created=api_response.get("dateCreated", ""),
        )

    def __str__(self):
        return (
            f"Trade({self.listing_name}, shares={self.number_of_shares}, "
            f"P/L={self.profit_loss:.2f} ({self.profit_loss_percentage:.2%}))"
        )

    def __repr__(self):
        return self.__str__()


class TradeStats:
    """
    Trade statistics accessor.

    Provides methods to retrieve trading performance data.
    """

    def __init__(self, client: "Client"):
        self.client = client

    def get_summary(
        self,
        securities_account_id: Optional[str] = None,
        security_identifier: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> TradeSummary:
        """
        Get trade statistics summary.

        Args:
            securities_account_id: Optional securities account ID to filter by
            security_identifier: Optional security identifier to filter by
            start_date: Optional start date filter (ISO format)
            end_date: Optional end date filter (ISO format)

        Returns:
            TradeSummary with aggregated trade statistics
        """
        params = {}
        if securities_account_id:
            params["securitiesAccountId"] = securities_account_id
        if security_identifier:
            params["securityIdentifier"] = security_identifier
        if start_date:
            params["startDate"] = start_date
        if end_date:
            params["endDate"] = end_date

        response = self.client.request("GET", "api/v2/trades/stats/summary", params=params)
        return TradeSummary.initialize_from_api_response(response.json())

    def get_best_trade(
        self,
        securities_account_id: Optional[str] = None,
        security_identifier: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> Optional[Trade]:
        """
        Get the best performing trade (highest profit).

        Args:
            securities_account_id: Optional securities account ID to filter by
            security_identifier: Optional security identifier to filter by
            start_date: Optional start date filter (ISO format)
            end_date: Optional end date filter (ISO format)

        Returns:
            Trade with highest profit, or None if no trades found
        """
        params = {}
        if securities_account_id:
            params["securitiesAccountId"] = securities_account_id
        if security_identifier:
            params["securityIdentifier"] = security_identifier
        if start_date:
            params["startDate"] = start_date
        if end_date:
            params["endDate"] = end_date

        response = self.client.request("GET", "api/v2/trades/stats/best", params=params)
        if response.status_code == 200 and response.json():
            return Trade.initialize_from_api_response(response.json())
        return None

    def get_worst_trade(
        self,
        securities_account_id: Optional[str] = None,
        security_identifier: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> Optional[Trade]:
        """
        Get the worst performing trade (biggest loss).

        Args:
            securities_account_id: Optional securities account ID to filter by
            security_identifier: Optional security identifier to filter by
            start_date: Optional start date filter (ISO format)
            end_date: Optional end date filter (ISO format)

        Returns:
            Trade with biggest loss, or None if no trades found
        """
        params = {}
        if securities_account_id:
            params["securitiesAccountId"] = securities_account_id
        if security_identifier:
            params["securityIdentifier"] = security_identifier
        if start_date:
            params["startDate"] = start_date
        if end_date:
            params["endDate"] = end_date

        response = self.client.request("GET", "api/v2/trades/stats/worst", params=params)
        if response.status_code == 200 and response.json():
            return Trade.initialize_from_api_response(response.json())
        return None

    def get_winning_trades(
        self,
        securities_account_id: Optional[str] = None,
        security_identifier: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        page: int = 0,
        size: int = 20,
        sort: Optional[str] = None,
    ) -> List[Trade]:
        """
        Get all profitable trades with pagination.

        Args:
            securities_account_id: Optional securities account ID to filter by
            security_identifier: Optional security identifier to filter by
            start_date: Optional start date filter (ISO format)
            end_date: Optional end date filter (ISO format)
            page: Page number (0-indexed)
            size: Page size
            sort: Sort order (e.g., "profitLoss,desc")

        Returns:
            List of profitable trades
        """
        params = {"page": page, "size": size}
        if securities_account_id:
            params["securitiesAccountId"] = securities_account_id
        if security_identifier:
            params["securityIdentifier"] = security_identifier
        if start_date:
            params["startDate"] = start_date
        if end_date:
            params["endDate"] = end_date
        if sort:
            params["sort"] = sort

        response = self.client.request("GET", "api/v2/trades/stats/wins", params=params)
        data = response.json()

        # Handle paginated response
        content = data.get("content", data) if isinstance(data, dict) else data
        if isinstance(content, list):
            return [Trade.initialize_from_api_response(item) for item in content]
        return []

    def get_losing_trades(
        self,
        securities_account_id: Optional[str] = None,
        security_identifier: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        page: int = 0,
        size: int = 20,
        sort: Optional[str] = None,
    ) -> List[Trade]:
        """
        Get all losing trades with pagination.

        Args:
            securities_account_id: Optional securities account ID to filter by
            security_identifier: Optional security identifier to filter by
            start_date: Optional start date filter (ISO format)
            end_date: Optional end date filter (ISO format)
            page: Page number (0-indexed)
            size: Page size
            sort: Sort order (e.g., "profitLoss,asc")

        Returns:
            List of losing trades
        """
        params = {"page": page, "size": size}
        if securities_account_id:
            params["securitiesAccountId"] = securities_account_id
        if security_identifier:
            params["securityIdentifier"] = security_identifier
        if start_date:
            params["startDate"] = start_date
        if end_date:
            params["endDate"] = end_date
        if sort:
            params["sort"] = sort

        response = self.client.request("GET", "api/v2/trades/stats/losses", params=params)
        data = response.json()

        # Handle paginated response
        content = data.get("content", data) if isinstance(data, dict) else data
        if isinstance(content, list):
            return [Trade.initialize_from_api_response(item) for item in content]
        return []

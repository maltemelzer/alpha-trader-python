from __future__ import annotations

from pydantic import BaseModel
from typing import Union, Dict, List
import requests
import os

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from alpha_trader.miner import Miner
    from alpha_trader.listing import Listing
    from alpha_trader.price.price_spread import PriceSpread
    from alpha_trader.user import User
    from alpha_trader.securities_account import SecuritiesAccount
    from alpha_trader.bonds import Bond
    from alpha_trader.company import Company
    from alpha_trader.order import Order
    from alpha_trader.trade_stats import TradeStats, TradeSummary, Trade
    from alpha_trader.order_log import OrderLogEntry
    from alpha_trader.highscore import UserHighscoreEntry, CompanyHighscoreEntry, AllianceHighscoreEntry
    from alpha_trader.index import Index, CompactIndex
    from alpha_trader.warrant import Warrant
    from alpha_trader.historical_data import HistorizedCompanyData, HistorizedListingData
    from alpha_trader.notification import Notification
    from alpha_trader.system_bond import SystemBond

from alpha_trader.logging import logger


class Client(BaseModel):
    """
    Client for interacting with the Alpha Trader API.

    Example:
        Authenticate and get a personal token:

        ```python

            >>> from alpha_trader.client import Client
            >>> client = Client(
            ...     base_url="https://stable.alpha-trader.com",
            ...     username="YOUR_USERNAME",
            ...     password="YOUR_PASSWORD",
            ...     partner_id="YOUR_PARTNER_ID")
            >>> client.login()
            2023-04-29 09:34:54,872 - alpha_trader.logging - INFO - Client successfully authenticated.
            >>> client.authenticated
            True
        ```

        ```python
        from alpha_trader.client import Client

        ```

    """

    base_url: str
    username: str
    password: str
    partner_id: str
    token: Union[str, None] = None
    authenticated: bool = False

    def login(self) -> str:
        """
        Login to the API and get a token.

        Returns:
            Token string
        """
        url = os.path.join(self.base_url, "user/token/")

        payload = {
            "username": self.username,
            "password": self.password,
            "partnerId": self.partner_id,
        }

        response = requests.request("POST", url, data=payload)

        self.token = response.json()["message"]
        self.authenticated = True

        logger.info("Client successfully authenticated.")

        return self.token

    def __get_headers(self):
        """"""
        headers = {"Authorization": f"Bearer {self.token}"}

        return headers

    def request(
            self, method: str, endpoint: str, data: Dict = None, json: Dict = None, additional_headers: Dict = None, params: Dict = None
    ) -> requests.Response:
        """Make a request using the authenticated client. This method is mainly used internally by other classes
        to retrieve more information from the API.

        Example:
            ```python
            >>> response = client.request("GET", "api/user")
            >>> user_information = response.json()
            >>> user_information["username"]
            Malte

        Args:
            body: body parameters
            additional_headers: Additional headers to be added to the request
            method: HTTP method
            endpoint: Endpoint
            data: Data

        Returns:
            HTTP Response
        """

        url = os.path.join(self.base_url, endpoint)

        if not self.authenticated:
            raise Exception("Client is not authenticated.")

        if additional_headers is None:
            headers = self.__get_headers()
        else:
            headers = self.__get_headers() | additional_headers

        response = requests.request(
            method, url, data=data, headers=headers, params=params, json=json
        )

        return response

    def get_user(self) -> User:
        """Get the user information for the authenticated user.
        Example:
            ```python
            >>> user = client.get_user()
            >>> user.username
            'Malte'
            >>> user.companies
            [Company(name=Argo, security_identifier=STAD9A0F12), Company(name=Argo2, security_identifier=STA8D0230B)]
            >>> user.securities_accounts
            SecuritiesAccount(id=7b3f6182-be88-4b98-aa75-4c2fd10487ae)
            ```

        Returns:
            User
        """
        from alpha_trader.user import User

        response = self.request("GET", "api/user")

        return User.initialize_from_api_response(response.json(), self)

    def get_miner(self) -> Miner:
        """Get the miner information for the authenticated user.
        :return: Miner
        """
        from alpha_trader.miner import Miner

        url = os.path.join(self.base_url, "api/v2/my/miner")

        response = requests.get(url, headers=self.__get_headers())

        return Miner.from_api_response(response.json(), client=self)

    def get_listing(self, security_identifier: str) -> Listing:
        """Get the listing information for a security.
        :param security_identifier: Security identifier
        :return: Listing
        """
        from alpha_trader.listing import Listing

        response = self.request("GET", f"api/listings/{security_identifier}")

        return Listing.initialize_from_api_response(response.json(), client=self)

    def get_price_spread(self, security_identifier: str) -> PriceSpread:
        """Get the price spread for a security.
        :param security_identifier: Security identifier
        :return: Price spread
        """
        from alpha_trader.price.price_spread import PriceSpread

        response = self.request("GET", f"api/pricespreads/{security_identifier}")

        return PriceSpread.initialize_from_api_response(response.json(), client=self)

    def get_securities_account(self, securities_account_id: str) -> SecuritiesAccount:
        """Get the securities account for a given ID.
        :param securities_account_id: Securities account ID
        :return: Securities account
        """
        from alpha_trader.securities_account import SecuritiesAccount

        response = self.request(
            "GET", f"api/v2/securitiesaccountdetails/{securities_account_id}"
        )

        return SecuritiesAccount.initialize_from_api_response(
            response.json(), client=self
        )

    def filter_listings(self, filter_id: str = None, filter_definition: Dict = None) -> List[PriceSpread]:
        """

        Returns:
            Price Spreads

        """
        from alpha_trader.price.price_spread import PriceSpread

        if filter_definition is None:
            filter_definition = {}

        if filter_id is None:
            params = None
        else:
            params = {"filterId": filter_id}

        response = self.request(
            "POST",
            "api/v2/filter/pricespreads",
            json=filter_definition,
            additional_headers={"Content-Type": "application/json"},
            params=params
        )

        return [
            PriceSpread.initialize_from_filter_api_response(item, client=self) for item in response.json()["results"]
        ]

    def get_bond(self, security_identifier: str, price_spread: Union[PriceSpread, None] = None) -> Bond:
        """
            Get the bond information for a security.

        Args:
            price_spread: manually set the price spread
            security_identifier: Security identifier

        Returns:
            Bond
        """
        from alpha_trader.bonds import Bond

        response = self.request("GET", f"api/bonds/securityidentifier/{security_identifier}")

        Bond.update_forward_refs()

        return Bond.initialize_from_api_response(response.json(), client=self, price_spread=price_spread)

    def get_company(self, security_identifier: str) -> Company:
        """
            Get the company information for a security.

        Args:
            security_identifier: Security identifier

        Returns:
            Company
        """
        from alpha_trader.company import Company

        response = self.request("GET", f"api/companies/securityIdentifier/{security_identifier}")

        return Company.initialize_from_api_response(response.json(), client=self)

    def get_order(self, order_id: str) -> Order:
        """
            Get the order information for a given order ID.

        Args:
            order_id: Order ID

        Returns:
            Order
        """
        from alpha_trader.order import Order

        response = self.request("GET", f"api/securityorders//{order_id}")

        return Order.initialize_from_api_response(response.json(), client=self)

    def get_bonds(self, page: int, search: str, page_size: int):
        pass

    def register_user(self, username: str, password: str, email: str, locale: str = None) -> User:
        """
            Register a new user
        Args:
            username: Username
            password: Password
            email: Email
            locale: Locale

        Returns:
            User
        """
        from alpha_trader.user import User

        data = {
            "username": username,
            "password": password,
            "emailAddress": email,
            "locale": locale,
        }

        response = requests.post(f"{self.base_url}/user/register", data=data)
        if response.status_code != 201:
            raise Exception(response.text)

        self.login()

        return User.initialize_from_api_response(response.json(), self)

    # Trade Statistics

    @property
    def trade_stats(self) -> "TradeStats":
        """
        Get trade statistics accessor for analyzing trading performance.

        Returns:
            TradeStats instance for accessing trade statistics

        Example:
            >>> summary = client.trade_stats.get_summary()
            >>> print(f"Win rate: {summary.win_rate:.2%}")
            >>> best_trade = client.trade_stats.get_best_trade()
        """
        from alpha_trader.trade_stats import TradeStats
        return TradeStats(self)

    # Order Logs

    def get_order_logs(
        self,
        securities_account_id: str = None,
        search: str = None,
        page: int = 0,
        size: int = 20,
        sort: str = None,
    ) -> List["OrderLogEntry"]:
        """
        Get security order logs (trade history).

        Args:
            securities_account_id: Optional securities account ID to filter by
            search: Optional search string
            page: Page number (0-indexed)
            size: Page size
            sort: Sort order (e.g., "date,desc")

        Returns:
            List of order log entries
        """
        from alpha_trader.order_log import get_order_logs
        return get_order_logs(self, securities_account_id, search, page, size, sort)

    def get_order_logs_by_security(
        self,
        security_identifier: str,
        page: int = 0,
        size: int = 20,
        sort: str = None,
    ) -> List["OrderLogEntry"]:
        """
        Get security order logs for a specific security.

        Args:
            security_identifier: Security identifier (ASIN)
            page: Page number (0-indexed)
            size: Page size
            sort: Sort order (e.g., "date,desc")

        Returns:
            List of order log entries for the security
        """
        from alpha_trader.order_log import get_order_logs_by_security
        return get_order_logs_by_security(self, security_identifier, page, size, sort)

    # Highscores

    def get_user_highscores(
        self,
        highscore_type: str = "NETWORTH",
        page: int = 0,
        size: int = 20,
        sort: str = None,
    ) -> List["UserHighscoreEntry"]:
        """
        Get user highscore leaderboard.

        Args:
            highscore_type: Type of highscore (NETWORTH, BOOK_VALUE, CASH, etc.)
            page: Page number (0-indexed)
            size: Page size
            sort: Sort order

        Returns:
            List of user highscore entries
        """
        from alpha_trader.highscore import get_user_highscores
        return get_user_highscores(self, highscore_type, page, size, sort)

    def get_company_highscores(
        self,
        highscore_type: str = "BOOK_VALUE",
        page: int = 0,
        size: int = 20,
        sort: str = None,
    ) -> List["CompanyHighscoreEntry"]:
        """
        Get company highscore leaderboard.

        Args:
            highscore_type: Type of highscore (BOOK_VALUE, CASH, etc.)
            page: Page number (0-indexed)
            size: Page size
            sort: Sort order

        Returns:
            List of company highscore entries
        """
        from alpha_trader.highscore import get_company_highscores
        return get_company_highscores(self, highscore_type, page, size, sort)

    def get_alliance_highscores(
        self,
        page: int = 0,
        size: int = 20,
        sort: str = None,
    ) -> List["AllianceHighscoreEntry"]:
        """
        Get alliance highscore leaderboard.

        Args:
            page: Page number (0-indexed)
            size: Page size
            sort: Sort order

        Returns:
            List of alliance highscore entries
        """
        from alpha_trader.highscore import get_alliance_highscores
        return get_alliance_highscores(self, page, size, sort)

    # Indexes

    def get_indexes(
        self,
        page: int = 0,
        size: int = 20,
        sort: str = None,
    ) -> List["CompactIndex"]:
        """
        Get list of all market indexes.

        Args:
            page: Page number (0-indexed)
            size: Page size
            sort: Sort order

        Returns:
            List of compact index views
        """
        from alpha_trader.index import get_indexes
        return get_indexes(self, page, size, sort)

    def get_index(self, security_identifier: str) -> "Index":
        """
        Get detailed index information including members.

        Args:
            security_identifier: Index security identifier

        Returns:
            Full index with members
        """
        from alpha_trader.index import get_index
        return get_index(self, security_identifier)

    # Warrants

    def get_warrants(
        self,
        underlying_asin: str = None,
        page: int = 0,
        size: int = 20,
        sort: str = None,
    ) -> List["Warrant"]:
        """
        Get list of warrants.

        Args:
            underlying_asin: Optional filter by underlying security identifier
            page: Page number (0-indexed)
            size: Page size
            sort: Sort order

        Returns:
            List of warrants
        """
        from alpha_trader.warrant import get_warrants
        return get_warrants(self, underlying_asin, page, size, sort)

    def get_warrant(self, warrant_id: str) -> "Warrant":
        """
        Get warrant by ID.

        Args:
            warrant_id: Warrant ID

        Returns:
            Warrant details
        """
        from alpha_trader.warrant import get_warrant
        return get_warrant(self, warrant_id)

    # Historical Data

    def get_company_history(
        self,
        security_identifier: str,
        page: int = 0,
        size: int = 100,
        sort: str = None,
    ) -> List["HistorizedCompanyData"]:
        """
        Get historical company data.

        Args:
            security_identifier: Security identifier (ASIN)
            page: Page number (0-indexed)
            size: Page size
            sort: Sort order (e.g., "date,desc")

        Returns:
            List of historical company data points
        """
        from alpha_trader.historical_data import get_company_history
        return get_company_history(self, security_identifier, page, size, sort)

    def get_listing_history(
        self,
        security_identifier: str,
        page: int = 0,
        size: int = 100,
        sort: str = None,
    ) -> List["HistorizedListingData"]:
        """
        Get historical listing (price) data - OHLC data.

        Args:
            security_identifier: Security identifier (ASIN)
            page: Page number (0-indexed)
            size: Page size
            sort: Sort order (e.g., "date,desc")

        Returns:
            List of historical listing data points (OHLC)
        """
        from alpha_trader.historical_data import get_listing_history
        return get_listing_history(self, security_identifier, page, size, sort)

    # Notifications

    def get_notifications(
        self,
        is_read: bool = None,
        search: str = None,
        page: int = 0,
        size: int = 20,
        sort: str = None,
    ) -> List["Notification"]:
        """
        Get user notifications.

        Args:
            is_read: Filter by read status (None for all)
            search: Optional search string
            page: Page number (0-indexed)
            size: Page size
            sort: Sort order (e.g., "date,desc")

        Returns:
            List of notifications
        """
        from alpha_trader.notification import get_notifications
        return get_notifications(self, is_read, search, page, size, sort)

    def get_unread_notification_count(self) -> int:
        """
        Get count of unread notifications.

        Returns:
            Number of unread notifications
        """
        from alpha_trader.notification import get_unread_count
        return get_unread_count(self)

    def mark_all_notifications_as_read(self, search: str = None) -> bool:
        """
        Mark all notifications as read.

        Args:
            search: Optional search filter to limit which notifications are marked

        Returns:
            True if successful
        """
        from alpha_trader.notification import mark_all_as_read
        return mark_all_as_read(self, search)

    # System Bonds

    def get_system_bonds(self) -> List["SystemBond"]:
        """
        Get all system bonds.

        Returns:
            List of system bonds
        """
        from alpha_trader.system_bond import get_system_bonds
        return get_system_bonds(self)

    def get_system_bond(self, bond_id: str) -> "SystemBond":
        """
        Get system bond by ID.

        Args:
            bond_id: Bond ID

        Returns:
            System bond details
        """
        from alpha_trader.system_bond import get_system_bond
        return get_system_bond(self, bond_id)

    def get_system_bond_by_security(self, security_identifier: str) -> "SystemBond":
        """
        Get system bond by security identifier.

        Args:
            security_identifier: Security identifier

        Returns:
            System bond details
        """
        from alpha_trader.system_bond import get_system_bond_by_security
        return get_system_bond_by_security(self, security_identifier)

    def get_main_interest_rate(self) -> float:
        """
        Get the current main interest rate.

        Returns:
            Current main interest rate
        """
        from alpha_trader.system_bond import get_main_interest_rate
        return get_main_interest_rate(self)

    def get_average_bond_interest_rate(self) -> float:
        """
        Get the average bond interest rate.

        Returns:
            Average bond interest rate
        """
        from alpha_trader.system_bond import get_average_bond_interest_rate
        return get_average_bond_interest_rate(self)

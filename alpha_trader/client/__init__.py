from __future__ import annotations

from pydantic import BaseModel
from typing import Optional, Union, Dict, List
from urllib.parse import urljoin
import requests

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

from alpha_trader.logging import logger
from alpha_trader.exceptions import (
    AuthenticationError,
    NotAuthenticatedError,
    APIError,
    NotFoundError,
    ValidationError,
    PermissionError as APIPermissionError,
)


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

        Raises:
            AuthenticationError: If authentication fails due to invalid credentials
        """
        url = self._build_url("user/token/")

        payload = {
            "username": self.username,
            "password": self.password,
            "partnerId": self.partner_id,
        }

        response = requests.request("POST", url, data=payload)

        if response.status_code == 401:
            raise AuthenticationError("Invalid credentials", status_code=401)
        elif response.status_code == 403:
            raise AuthenticationError("Access forbidden - check partner ID", status_code=403)
        elif response.status_code >= 400:
            raise AuthenticationError(
                f"Authentication failed: {response.text}",
                status_code=response.status_code
            )

        try:
            data = response.json()
            self.token = data["message"]
        except (KeyError, ValueError) as e:
            raise AuthenticationError(f"Invalid response from server: {e}")

        self.authenticated = True
        logger.info("Client successfully authenticated.")

        return self.token

    def _build_url(self, endpoint: str) -> str:
        """Build a full URL from the base URL and endpoint.

        Args:
            endpoint: The API endpoint path

        Returns:
            The full URL
        """
        base = self.base_url if self.base_url.endswith("/") else f"{self.base_url}/"
        return urljoin(base, endpoint)

    def __get_headers(self):
        """"""
        headers = {"Authorization": f"Bearer {self.token}"}

        return headers

    def request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict] = None,
        json: Optional[Dict] = None,
        additional_headers: Optional[Dict] = None,
        params: Optional[Dict] = None,
        raise_for_status: bool = True,
    ) -> requests.Response:
        """Make a request using the authenticated client.

        This method is mainly used internally by other classes to retrieve more
        information from the API.

        Example:
            ```python
            >>> response = client.request("GET", "api/user")
            >>> user_information = response.json()
            >>> user_information["username"]
            Malte
            ```

        Args:
            method: HTTP method (GET, POST, PUT, DELETE, etc.)
            endpoint: API endpoint path
            data: Form data to send in the request body
            json: JSON data to send in the request body
            additional_headers: Additional headers to be added to the request
            params: Query parameters
            raise_for_status: If True, raise an exception for error status codes

        Returns:
            HTTP Response

        Raises:
            NotAuthenticatedError: If the client is not authenticated
            NotFoundError: If the resource is not found (404)
            ValidationError: If the request is invalid (400)
            APIPermissionError: If permission is denied (403)
            APIError: For other API errors
        """
        url = self._build_url(endpoint)

        if not self.authenticated:
            raise NotAuthenticatedError()

        if additional_headers is None:
            headers = self.__get_headers()
        else:
            headers = self.__get_headers() | additional_headers

        response = requests.request(
            method, url, data=data, headers=headers, params=params, json=json
        )

        if raise_for_status:
            self._handle_response_errors(response, endpoint)

        return response

    def _handle_response_errors(self, response: requests.Response, endpoint: str) -> None:
        """Handle error responses from the API.

        Args:
            response: The HTTP response
            endpoint: The API endpoint that was called

        Raises:
            NotFoundError: If the resource is not found (404)
            ValidationError: If the request is invalid (400)
            APIPermissionError: If permission is denied (403)
            AuthenticationError: If authentication failed (401)
            APIError: For other API errors
        """
        if response.status_code < 400:
            return

        try:
            error_data = response.json()
            message = error_data.get("message", str(error_data))
        except ValueError:
            error_data = None
            message = response.text or f"HTTP {response.status_code}"

        if response.status_code == 400:
            raise ValidationError(message, response=error_data, endpoint=endpoint)
        elif response.status_code == 401:
            raise AuthenticationError(message, status_code=401)
        elif response.status_code == 403:
            raise APIPermissionError(message, response=error_data, endpoint=endpoint)
        elif response.status_code == 404:
            raise NotFoundError(message, response=error_data, endpoint=endpoint)
        else:
            raise APIError(
                message,
                status_code=response.status_code,
                response=error_data,
                endpoint=endpoint,
            )

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

        Returns:
            Miner

        Raises:
            NotAuthenticatedError: If the client is not authenticated
            APIError: If the API request fails
        """
        from alpha_trader.miner import Miner

        response = self.request("GET", "api/v2/my/miner")

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

    def register_user(
        self, username: str, password: str, email: str, locale: Optional[str] = None
    ) -> User:
        """Register a new user.

        Args:
            username: Username
            password: Password
            email: Email
            locale: Locale (optional)

        Returns:
            User

        Raises:
            ValidationError: If the registration data is invalid
            APIError: If registration fails
        """
        from alpha_trader.user import User

        data = {
            "username": username,
            "password": password,
            "emailAddress": email,
            "locale": locale,
        }

        url = self._build_url("user/register")
        response = requests.post(url, data=data)

        if response.status_code == 400:
            try:
                error_data = response.json()
                message = error_data.get("message", response.text)
            except ValueError:
                message = response.text
            raise ValidationError(message, endpoint="user/register")
        elif response.status_code != 201:
            raise APIError(
                response.text,
                status_code=response.status_code,
                endpoint="user/register",
            )

        self.login()

        return User.initialize_from_api_response(response.json(), self)

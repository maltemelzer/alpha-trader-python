from __future__ import annotations

from pydantic import BaseModel
from typing import Union, Dict
import requests
import os

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from alpha_trader.miner import Miner
    from alpha_trader.listing import Listing
    from alpha_trader.price.price_spread import PriceSpread
    from alpha_trader.user import User
    from alpha_trader.securities_account import SecuritiesAccount

from alpha_trader.logging import logger


class Client(BaseModel):
    """
        Client for interacting with the API.
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
        Returns: Token

        """
        url = os.path.join(self.base_url, "user/token/")

        payload = {
            "username": self.username,
            "password": self.password,
            "partnerId": self.partner_id
        }

        response = requests.request("POST", url, data=payload)

        self.token = response.json()["message"]
        self.authenticated = True

        logger.info(f"Client successfully authenticated.")

        return self.token

    def get_headers(self):
        headers = {
            "Authorization": f"Bearer {self.token}"
        }

        return headers

    def request(self, method: str, endpoint: str, data: Dict = None) -> requests.Response:
        """ Make a request using the authenticated client.

        Args:
            method: HTTP method
            endpoint: Endpoint
            data: Data

        Returns: HTTP Response
        """

        url = os.path.join(self.base_url, endpoint)

        if not self.authenticated:
            raise Exception("Client is not authenticated.")

        response = requests.request(method, url, data=data, headers=self.get_headers())

        return response

    def get_user(self) -> User:
        """ Get the user information for the authenticated user.
        :return: User
        """
        from alpha_trader.user import User
        response = self.request("GET", "api/user")

        return User.initialize_from_api_response(response.json(), self)

    def get_miner(self) -> Miner:
        """ Get the miner information for the authenticated user.
        :return: Miner
        """
        from alpha_trader.miner import Miner
        url = os.path.join(self.base_url, "api/v2/my/miner")

        response = requests.get(url, headers=self.get_headers())

        return Miner.from_api_response(response.json(), client=self)

    def get_listing(self, security_identifier: str) -> Listing:
        """ Get the listing information for a security.
        :param security_identifier: Security identifier
        :return: Listing
        """
        from alpha_trader.listing import Listing
        response = self.request("GET", f"/api/listings/{security_identifier}")

        return Listing.from_api_response(response.json(), client=self)

    def get_price_spread(self, security_identifier: str) -> PriceSpread:
        """ Get the price spread for a security.
        :param security_identifier: Security identifier
        :return: Price spread
        """
        from alpha_trader.price.price_spread import PriceSpread
        response = self.request("GET", f"api/pricespreads/{security_identifier}")

        return PriceSpread.initialize_from_api_response(response.json(), client=self)

    def get_securities_account(self, securities_account_id: str) -> SecuritiesAccount:
        """ Get the securities account for a given ID.
        :param securities_account_id: Securities account ID
        :return: Securities account
        """
        from alpha_trader.securities_account import SecuritiesAccount
        response = self.request("GET", f"api/v2/securitiesaccountdetails/{securities_account_id}")

        return SecuritiesAccount.initialize_from_api_response(response.json(), client=self)


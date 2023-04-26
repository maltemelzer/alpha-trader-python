from pydantic import BaseModel
from typing import Union, Dict
import requests
import os

from alpha_trader.logging import logger


class Client(BaseModel):
    base_url: str
    username: str
    password: str
    partner_id: str
    token: Union[str, None] = None
    authenticated: bool = False

    def login(self) -> str:
        """
        Login to the API and get a token.
        :return: Token
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
        """ Send a request to the API.

        :param method: HTTP method
        :param endpoint: Endpoint
        :param data: Data
        :return: Response
        """
        url = os.path.join(self.base_url, endpoint)

        if not self.authenticated:
            raise Exception("Client is not authenticated.")

        response = requests.request(method, url, data=data, headers=self.get_headers())

        return response

    def get_user(self):
        """ Get the user information for the authenticated user.
        :return: User
        """
        response = self.request("GET", "api/user")

        return User.initialize_from_api_response(response.json(), self)

    def get_miner(self):
        """ Get the miner information for the authenticated user.
        :return: Miner
        """
        url = os.path.join(self.base_url, "api/v2/my/miner")

        response = requests.get(url, headers=self.get_headers())

        return Miner.from_api_response(response.json(), client=self)

    def get_listing(self, security_identifier: str):
        """ Get the listing information for a security.
        :param security_identifier: Security identifier
        :return: Listing
        """
        response = self.request("GET", f"/api/listings/{security_identifier}")

        return Listing.from_api_response(response.json(), client=self)

    def get_price_spread(self, security_identifier: str):
        """ Get the price spread for a security.
        :param security_identifier: Security identifier
        :return: Price spread
        """
        response = self.request("GET", f"api/pricespreads/{security_identifier}")

        return PriceSpread.initialize_from_api_response(response.json(), client=self)


from alpha_trader.miner import Miner
from alpha_trader.listing import Listing
from alpha_trader.price.price_spread import PriceSpread
from alpha_trader.user import User

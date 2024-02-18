from pydantic import BaseModel
from typing import Dict, List

from alpha_trader.client import Client
from alpha_trader.portfolio import Portfolio
from alpha_trader.order import Order


class SecuritiesAccount(BaseModel):
    """
    The SecuritiesAccount model represents a securities account in the trading system.
    
    Attributes:
        clearing_account_id (str): The ID of the clearing account associated with this securities account.
        id (str): The unique ID of the securities account.
        private_account (bool): A flag indicating whether the securities account is private.
        version (int): The version of the securities account.
        client (Client): The client associated with the securities account, used for API interactions.
    """

    clearing_account_id: str
    id: str
    private_account: bool
    version: int
    client: Client

    @staticmethod
    def initialize_from_api_response(api_response: Dict, client: Client):
        return SecuritiesAccount(
            clearing_account_id=api_response["clearingAccountId"],
            id=api_response["id"],
            private_account=api_response["privateAccount"],
            version=api_response["version"],
            client=client,
        )

    def __str__(self):
        return f"SecuritiesAccount(id={self.id})"

    def __repr__(self):
        return self.__str__()

    @property
    def portfolio(self) -> Portfolio:
        """
        Retrieve the portfolio of this securities account
        Returns:
            Portfolio: The portfolio associated with this securities account
        """
        response = self.client.request("GET", f"api/portfolios/{self.id}")

        return Portfolio.initialize_from_api_response(response.json(), self.client)

    @property
    def orders(self) -> List[Order]:
        """
            Orders for this securities account
        Returns:
            List of orders
        """
        response = self.client.request(
            "GET", f"api/securityorders/securitiesaccount/{self.id}"
        )

        return [
            Order.initialize_from_api_response(res, self.client)
            for res in response.json()
        ]

    def delete_all_orders(self):
        response = self.client.request("DELETE", f"api/securityorders", params={"owner": self.id})

        if response.status_code > 205:
            print(response.text)

        return response.status_code

    def order(
        self,
        action: str,
        order_type: str,
        quantity: int,
        security_identifier: str,
        price: float = None
    ) -> Order:
        """Create an order for this securities account

        Args:
            action: action of the order "BUY" or "SELL"
            order_type: order type "LIMIT" or "MARKET"
            price: price of the order
            quantity: number of shares
            security_identifier: security identifier of the order

        Returns:
            Order
        """
        return Order.create(
            action=action,
            order_type=order_type,
            price=price,
            quantity=quantity,
            security_identifier=security_identifier,
            client=self.client,
            owner_securities_account_id=self.id,
        )

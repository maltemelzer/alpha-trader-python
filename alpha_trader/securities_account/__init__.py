from pydantic import BaseModel
from typing import Dict, List

from alpha_trader.client import Client
from alpha_trader.portfolio import Portfolio
from alpha_trader.order import Order


class SecuritiesAccount(BaseModel):
    """
    Securities account model

    Attributes:
        clearing_account_id: Clearing account ID of the securities account
        id: securities account ID
        private_account: Flag if the securities account is private
        version: Version of the securities account
        client: Client of the securities account (for interaction with the API)
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
            Portfolio of this securities account
        Returns:
            Portfolio
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

    def order(
        self,
        action: str,
        order_type: str,
        price: float,
        quantity: int,
        security_identifier: str,
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

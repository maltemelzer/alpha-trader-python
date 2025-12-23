from pydantic import BaseModel
from typing import Dict, List, Optional

from alpha_trader.client import Client
from alpha_trader.portfolio import Portfolio
from alpha_trader.order import Order
from alpha_trader.exceptions import APIError
from alpha_trader.logging import logger


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

    def delete_all_orders(self) -> bool:
        """Delete all orders for this securities account.

        Returns:
            True if all orders were successfully deleted

        Raises:
            APIError: If the deletion fails
        """
        response = self.client.request(
            "DELETE", "api/securityorders", params={"owner": self.id}, raise_for_status=False
        )

        if response.status_code > 205:
            try:
                error_data = response.json()
                message = error_data.get("message", response.text)
            except ValueError:
                message = response.text
            logger.error(f"Failed to delete orders: {message}")
            raise APIError(
                message,
                status_code=response.status_code,
                endpoint="api/securityorders",
            )

        logger.info(f"Deleted all orders for account {self.id}")
        return True

    def order(
        self,
        action: str,
        order_type: str,
        quantity: int,
        security_identifier: str,
        price: Optional[float] = None,
        counter_party: Optional[str] = None,
    ) -> Order:
        """Create an order for this securities account.

        Args:
            action: Action of the order "BUY" or "SELL"
            order_type: Order type "LIMIT" or "MARKET"
            price: Price of the order
            quantity: Number of shares
            security_identifier: Security identifier of the order
            counter_party: Security account id of the counterparty

        Returns:
            Order

        Raises:
            OrderError: If the order creation fails
        """
        return Order.create(
            action=action,
            order_type=order_type,
            price=price,
            quantity=quantity,
            security_identifier=security_identifier,
            client=self.client,
            owner_securities_account_id=self.id,
            counter_party=counter_party,
        )

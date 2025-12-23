from pydantic import BaseModel, Field, ConfigDict
from typing import Dict, List, Optional

from alpha_trader.client import Client
from alpha_trader.price.price_spread import PriceSpread
from alpha_trader.listing import Listing
from alpha_trader.logging import logger


class Message(BaseModel):
    """Message model for order check results.

    Attributes:
        filled_string: The filled message string with substitutions applied
        message: The message template
        substitutions: List of values to substitute into the message
    """

    model_config = ConfigDict(populate_by_name=True)

    filled_string: str = Field(alias="filledString")
    message: str
    substitutions: List[str]

    @staticmethod
    def initialize_from_api_response(api_response: Dict) -> "Message":
        """Create a Message instance from an API response."""
        return Message(
            filled_string=api_response["filledString"],
            message=api_response["message"],
            substitutions=api_response["substitutions"],
        )


class OrderCheckResult(BaseModel):
    """Result of an order validation check.

    Attributes:
        failed: Whether the check failed
        msg: The message describing the result
        ok: Whether the order is OK to proceed
        concerning_params: List of parameter names that caused issues
    """

    model_config = ConfigDict(populate_by_name=True)

    failed: bool
    msg: Message
    ok: bool
    concerning_params: List[str] = Field(alias="concerningParams")

    @staticmethod
    def initialize_from_api_response(api_response: Dict) -> "OrderCheckResult":
        """Create an OrderCheckResult instance from an API response."""
        return OrderCheckResult(
            failed=api_response["failed"],
            msg=Message.initialize_from_api_response(api_response["msg"]),
            ok=api_response["ok"],
            concerning_params=api_response["concerningParams"],
        )


class Order(BaseModel):
    """Security order model.

    Represents a buy or sell order for securities in the trading system.

    Attributes:
        action: Order action - "BUY" or "SELL"
        check_result: Result of order validation check (if performed)
        committed_cash: Cash committed to this order
        counter_party: ID of the counterparty (for private orders)
        counter_party_name: Name of the counterparty
        creation_date: Timestamp when the order was created
        execution_price: Price at which the order was executed
        execution_volume: Volume that was executed
        good_after_date: Order becomes active after this date
        good_till_date: Order expires after this date
        hourly_change: Hourly price change for the order
        id: Unique identifier of the order
        listing: Listing information for the security
        next_hourly_change_date: Next scheduled hourly change date
        number_of_shares: Number of shares in the order
        owner: ID of the order owner
        owner_name: Name of the order owner
        price: Order price (for limit orders)
        private_counter_party: Whether the counterparty is private
        private_owner: Whether the owner is private
        security_identifier: Identifier of the security
        spread: Current price spread for the security
        type: Order type - "LIMIT" or "MARKET"
        uncommitted_cash: Uncommitted cash
        uncommitted_shares: Uncommitted shares
        version: Version for optimistic locking
        volume: Total order volume
        client: API client for making requests
    """

    action: str
    check_result: Optional[OrderCheckResult] = None
    committed_cash: float
    counter_party: Optional[str] = None
    counter_party_name: Optional[str] = None
    creation_date: int
    execution_price: Optional[float] = None
    execution_volume: Optional[float] = None
    good_after_date: Optional[int] = None
    good_till_date: Optional[int] = None
    hourly_change: Optional[int] = None
    id: str
    listing: Listing
    next_hourly_change_date: Optional[int] = None
    number_of_shares: int
    owner: str
    owner_name: str
    price: Optional[float] = None
    private_counter_party: Optional[bool] = None
    private_owner: bool
    security_identifier: str
    spread: Optional[PriceSpread] = None
    type: str
    uncommitted_cash: Optional[float] = None
    uncommitted_shares: int
    version: Optional[int] = None
    volume: Optional[float] = None
    client: Client

    @staticmethod
    def initialize_from_api_response(api_response: Dict, client: Client):
        return Order(
            action=api_response["action"],
            check_result=api_response["checkResult"],
            committed_cash=api_response["committedCash"],
            counter_party=api_response["counterParty"],
            counter_party_name=api_response["counterPartyName"],
            creation_date=api_response["creationDate"],
            execution_price=api_response["executionPrice"],
            execution_volume=api_response["executionVolume"],
            good_after_date=api_response["goodAfterDate"],
            good_till_date=api_response["goodTillDate"],
            hourly_change=api_response["hourlyChange"],
            id=api_response["id"],
            listing=Listing.initialize_from_api_response(
                api_response["listing"], client
            ),
            next_hourly_change_date=api_response["nextHourlyChangeDate"],
            number_of_shares=api_response["numberOfShares"],
            owner=api_response["owner"],
            owner_name=api_response["ownerName"],
            price=api_response["price"],
            private_counter_party=api_response["privateCounterParty"],
            private_owner=api_response["privateOwner"],
            security_identifier=api_response["securityIdentifier"],
            spread=PriceSpread.initialize_from_api_response(
                api_response["spread"], client
            )
            if type(api_response["spread"]) == dict
            else None,
            type=api_response["type"],
            uncommitted_cash=api_response["uncommittedCash"],
            uncommitted_shares=api_response["uncommittedShares"],
            version=api_response["version"],
            client=client,
        )

    def delete(self):
        response = self.client.request("DELETE", f"api/securityorders/{self.id}")

        return response.status_code == 200

    @staticmethod
    def create(
        action: str,
        quantity: int,
        client: Client,
        owner_securities_account_id: str,
        security_identifier: str,
        price: Optional[float] = None,
        good_after_date: Optional[int] = None,
        good_till_date: Optional[int] = None,
        order_type: str = "LIMIT",
        counter_party: Optional[str] = None,
        hourly_change: Optional[float] = None,
        check_order_only: bool = False,
    ) -> "Order":
        """Create a new order.

        Args:
            action: Security order action - "BUY" or "SELL"
            quantity: Number of shares to buy or sell
            client: Alpha Trader Client
            owner_securities_account_id: Securities Account ID of the owner
            security_identifier: Security identifier
            price: Limit price (required for LIMIT orders)
            good_after_date: Order becomes active after this date (premium feature)
            good_till_date: Order expires after this date (premium feature)
            order_type: Order type - "LIMIT" or "MARKET"
            counter_party: Securities Account ID of the counterparty (for private orders)
            hourly_change: Hourly price change for the order
            check_order_only: If True, only validate the order without creating it

        Returns:
            The created Order

        Raises:
            Exception: If order creation fails
        """
        data = {
            "action": action,
            "numberOfShares": quantity,
            "price": price,
            "goodAfterDate": good_after_date,
            "goodTillDate": good_till_date,
            "type": order_type,
            "counterparty": counter_party,
            "owner": owner_securities_account_id,
            "securityIdentifier": security_identifier,
            "checkOrderOnly": check_order_only,
            "hourlyChange": hourly_change,
        }

        response = client.request("POST", "api/securityorders", data=data)
        if response.status_code not in [200, 201]:
            logger.error(f"Order creation failed: {response.text}")
            raise Exception(f"Order creation failed: {response.text}")

        order = Order.initialize_from_api_response(response.json(), client)
        logger.info(f"Order created: {order}")
        return order

    def update(self):
        response = self.client.request("GET", f"api/securityorders/{self.id}")

        return Order.initialize_from_api_response(response.json(), self.client)

    def __str__(self):
        return (
            f"{self.action} {self.number_of_shares} {self.listing.name} @ {self.price}"
        )

    def __repr__(self):
        return self.__str__()

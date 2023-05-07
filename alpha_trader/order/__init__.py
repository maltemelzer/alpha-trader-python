from pydantic import BaseModel
from typing import Dict, List, Union

from alpha_trader.client import Client
from alpha_trader.price.price_spread import PriceSpread
from alpha_trader.listing import Listing


class Message(BaseModel):
    filledString: str
    message: str
    substitutions: List[str]

    @staticmethod
    def initialize_from_api_response(api_response: Dict):
        return Message(
            filledString=api_response["filledString"],
            message=api_response["message"],
            substitutions=api_response["substitutions"],
        )


class OrderCheckResult(BaseModel):
    failed: bool
    msg: Message
    ok: bool
    concerningParams: List[str]

    @staticmethod
    def initialize_from_api_response(api_response: Dict):
        return OrderCheckResult(
            failed=api_response["failed"],
            msg=Message.initialize_from_api_response(api_response["msg"]),
            ok=api_response["ok"],
            concerningParams=api_response["concerningParams"],
        )


class Order(BaseModel):
    action: str
    check_result: Union[OrderCheckResult, None]
    committed_cash: float
    counter_party: Union[str, None]
    counter_party_name: Union[str, None]
    creation_date: int
    execution_price: Union[float, None]
    execution_volume: Union[int, None]
    good_after_date: Union[int, None]
    good_till_date: Union[int, None]
    hourly_change: Union[int, None]
    id: str
    listing: Listing
    next_hourly_change_date: Union[int, None]
    number_of_shares: int
    owner: str
    owner_name: str
    price: float
    private_counter_party: Union[bool, None]
    private_owner: bool
    security_identifier: str
    spread: Union[PriceSpread, None]
    type: str
    uncommitted_cash: Union[float, None]
    uncommitted_shares: int
    version: Union[int, None]
    volume: Union[float, None]
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
        price: float,
        client: Client,
        owner_securities_account_id: str,
        security_identifier: str,
        good_after_date: int = None,
        good_till_date: int = None,
        order_type: str = "LIMIT",
        counter_party: str = None,
        hourly_change: float = None,
        check_order_only: bool = False,
    ) -> "Order":
        """Creates a new order.

        Args:
            client: Alpha Trader Client
            action: Security Order Action, either "BUY" or "SELL"
            quantity:  Number of shares to buy or sell
            price: Price
            good_after_date: Valid from date (premium feature)
            good_till_date: Valid until date (premium feature)
            order_type: Security Order Type, either "LIMIT" or "MARKET"
            counter_party: Securities Account ID of the counterparty
            owner_securities_account_id: Securities Account ID of the owner
            security_identifier: Security Identifier
            hourly_change: Hourly change of the order
            check_order_only: Only check the order, do not create it

        Returns:
            Order

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

        return Order.initialize_from_api_response(response.json(), client)

    def update(self):
        response = self.client.request("GET", f"api/securityorders/{self.id}")

        return Order.initialize_from_api_response(response.json(), self.client)

    def __str__(self):
        return (
            f"{self.action} {self.number_of_shares} {self.listing.name} @ {self.price}"
        )

    def __repr__(self):
        return self.__str__()

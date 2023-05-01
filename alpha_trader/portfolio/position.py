from pydantic import BaseModel
from typing import Dict

from alpha_trader.listing import Listing
from alpha_trader.price.price import Price
from alpha_trader.client import Client


class Position(BaseModel):
    average_buying_price: int
    committed_shares: int
    current_ask_price: int
    current_ask_size: int
    current_bid_price: int
    current_bid_size: int
    last_buying_price: int
    last_price: Price
    last_price_update: int
    listing: Listing
    number_of_shares: int
    security_identifier: str
    type: str
    volume: int
    client: Client

    @staticmethod
    def initialize_from_api_response(api_response: Dict, client: Client):
        return Position(
            average_buying_price=api_response["averageBuyingPrice"],
            committed_shares=api_response["committedShares"],
            current_ask_price=api_response["currentAskPrice"],
            current_ask_size=api_response["currentAskSize"],
            current_bid_price=api_response["currentBidPrice"],
            current_bid_size=api_response["currentBidSize"],
            last_buying_price=api_response["lastBuyingPrice"],
            last_price=Price.initialize_from_api_response(api_response["lastPrice"]),
            last_price_update=api_response["lastPriceUpdate"],
            listing=Listing.initialize_from_api_response(
                api_response["listing"], client
            ),
            number_of_shares=api_response["numberOfShares"],
            security_identifier=api_response["securityIdentifier"],
            type=api_response["type"],
            volume=api_response["volume"],
            client=client,
        )

    def __str__(self):
        return f"Position(security_identifier={self.security_identifier}, number_of_shares={self.number_of_shares}, " \
               f"value=${self.volume / 100}) "

    def __repr__(self):
        return self.__str__()

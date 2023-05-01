from pydantic import BaseModel
from typing import Dict
from typing import Union
from alpha_trader.listing import Listing
from alpha_trader.price.price import Price
from alpha_trader.client import Client


class PriceSpread(BaseModel):
    listing: Listing
    bid_price: float
    bid_size: int
    ask_price: float
    ask_size: int
    spread_abs: float
    spread_percent: float
    date: int
    last_price: Price
    end_date: Union[int, None]
    name: str
    security_identifier: str
    start_date: int
    type: str

    @staticmethod
    def initialize_from_api_response(api_response: Dict, client: Client):
        return PriceSpread(
            listing=Listing.initialize_from_api_response(
                api_response["listing"], client=client
            ),
            bid_price=api_response["bidPrice"],
            bid_size=api_response["bidSize"],
            ask_price=api_response["askPrice"],
            ask_size=api_response["askSize"],
            spread_abs=api_response["spreadAbs"],
            spread_percent=api_response["spreadPercent"],
            date=api_response["date"],
            last_price=Price.initialize_from_api_response(api_response["lastPrice"]),
            end_date=api_response["listing"]["endDate"],
            name=api_response["listing"]["name"],
            security_identifier=api_response["listing"]["securityIdentifier"],
            start_date=api_response["listing"]["startDate"],
            type=api_response["listing"]["type"],
        )

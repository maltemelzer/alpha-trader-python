from pydantic import BaseModel
from typing import Dict
from typing import Union
from alpha_trader.listing import Listing
from alpha_trader.price.price import Price
from alpha_trader.client import Client


class PriceSpread(BaseModel):
    listing: Listing
    bid_price: Union[float, None]
    bid_size: Union[int, None]
    ask_price: Union[float, None]
    ask_size: Union[int, None]
    spread_abs: Union[float, None]
    spread_percent: Union[float, None]
    date: Union[int, None]
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
            bid_price=api_response.get("bidPrice", None),
            bid_size=api_response.get("bidSize", None),
            ask_price=api_response.get("askPrice", None),
            ask_size=api_response.get("askSize", None),
            spread_abs=api_response.get("spreadAbs", None),
            spread_percent=api_response.get("spreadPercent", None),
            date=api_response["date"],
            last_price=Price.initialize_from_api_response(api_response["lastPrice"]),
            end_date=api_response["listing"]["endDate"],
            name=api_response["listing"]["name"],
            security_identifier=api_response["listing"]["securityIdentifier"],
            start_date=api_response["listing"]["startDate"],
            type=api_response["listing"]["type"],
        )

    @staticmethod
    def initialize_from_filter_api_response(api_response: Dict, client: Client):
        return PriceSpread(
            listing=Listing.initialize_from_api_response(
                api_response["listing"], client=client
            ),
            bid_price=api_response["price"].get("bidPrice", None),
            bid_size=api_response["price"].get("bidSize", None),
            ask_price=api_response["price"].get("askPrice", None),
            ask_size=api_response["price"].get("askSize", None),
            spread_abs=api_response["price"].get("spreadAbs", None),
            spread_percent=api_response["price"].get("spreadPercent", None),
            date=api_response["price"].get("date", None),
            last_price=Price.initialize_from_api_response(api_response["price"]["lastPrice"]),
            end_date=api_response["listing"].get("endDate", None),
            name=api_response["listing"]["name"],
            security_identifier=api_response["listing"]["securityIdentifier"],
            start_date=api_response["listing"]["startDate"],
            type=api_response["listing"]["type"],
        )

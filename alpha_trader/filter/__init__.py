from pydantic import BaseModel

from alpha_trader.listing import Listing
from alpha_trader.price.price_spread import PriceSpread
from alpha_trader.client import Client


class FilterResult(BaseModel):
    price_spread: PriceSpread
    listing: Listing

    @staticmethod
    def initialize_from_api_response(api_response: dict, client: Client):
        return FilterResult(
            price_spread=PriceSpread.initialize_from_api_response(api_response["priceSpread"], client=client),
            listing=Listing.initialize_from_api_response(api_response["listing"], client=client),
        )

    def __str__(self):
        return f"FilterResult(price_spread={self.price_spread.ask_price}, listing={self.listing.name})"

    def __repr__(self):
        return self.__str__()

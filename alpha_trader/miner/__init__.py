import logging

from pydantic import BaseModel
from typing import Dict
import os
import requests

from alpha_trader.owner import Owner
from alpha_trader.client import Client
from alpha_trader.logging import logger


class Miner(BaseModel):
    coins_per_hour: int
    id: str
    maximum_capacity: int
    next_level_coins_per_hour: int
    next_level_costs: int
    owner: Owner
    storage: int
    transferable_coins: int
    version: int
    client: Client

    @staticmethod
    def from_api_response(api_response: Dict, client: Client):
        return Miner(
            coins_per_hour=api_response["coinsPerHour"],
            id=api_response["id"],
            maximum_capacity=api_response["maximumCapacity"],
            next_level_coins_per_hour=api_response["nextLevelCoinsPerHour"],
            next_level_costs=api_response["nextLevelCosts"],
            owner=Owner.from_api_response(api_response["owner"]),
            storage=api_response["storage"],
            transferable_coins=api_response["transferableCoins"],
            version=api_response["version"],
            client=client
        )

    def update_from_api_response(self, api_response: Dict):
        self.coins_per_hour = api_response["coinsPerHour"]
        self.id = api_response["id"]
        self.maximum_capacity = api_response["maximumCapacity"]
        self.next_level_coins_per_hour = api_response["nextLevelCoinsPerHour"]
        self.next_level_costs = api_response["nextLevelCosts"]
        self.owner = Owner.from_api_response(api_response["owner"])
        self.storage = api_response["storage"]
        self.transferable_coins = api_response["transferableCoins"]
        self.version = api_response["version"]

    def transfer_coins(self):
        response = self.client.request("PUT", "api/v2/my/cointransfer")
        self.update_from_api_response(response.json())

        logger.info(f"Coins transferred. New transferable coins: {self.transferable_coins}")

        return response.json()

    def upgrade(self) -> Dict:
        """ Upgrade the miner to the next level.
        :return: API response
        """
        response = self.client.request("PUT", "api/v2/my/minerupgrade")
        self.update_from_api_response(response.json())

        logger.info(f"Miner upgraded. New coins per hour: {self.coins_per_hour}")
        logger.info(f"Next level costs: {self.next_level_costs}")
        logger.info(f"Next level coins per hour: {self.next_level_coins_per_hour}")

        return response.json()

    def __get_coin_bid_price(self):
        """ Get the coin bid price.
        :return: Coin bid price
        """
        return self.client.get_price_spread("ACALPHCOIN").bid_price

    @property
    def next_level_amortization_hours(self) -> int:
        """ Calculate the next level amortization.
        :return: Amortization
        """
        coin_bid_price = self.__get_coin_bid_price()
        additional_earnings_per_hour = (self.next_level_coins_per_hour - self.coins_per_hour) * coin_bid_price

        next_level_amortization_hours = self.next_level_costs // additional_earnings_per_hour

        logger.info(f"""Next level amortization hours: {
            next_level_amortization_hours
        } (or {
            next_level_amortization_hours / 24
        } days)""")

        return next_level_amortization_hours

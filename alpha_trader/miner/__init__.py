import logging

from pydantic import BaseModel
from typing import Dict
import os
import requests

from alpha_trader.owner import Owner
from alpha_trader.client import Client


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

        logging.info(f"Coins transferred. New transferable coins: {self.transferable_coins}")

        return response.json()

    def upgrade(self) -> Dict:
        """ Upgrade the miner to the next level.
        :return: API response
        """
        response = self.client.request("PUT", "api/v2/my/minerupgrade")
        self.update_from_api_response(response.json())

        logging.info(f"Miner upgraded. New coins per hour: {self.coins_per_hour}")
        logging.info(f"Next level costs: {self.next_level_costs}")
        logging.info(f"Next level coins per hour: {self.next_level_coins_per_hour}")

        return response.json()

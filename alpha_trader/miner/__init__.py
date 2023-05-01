from pydantic import BaseModel
from typing import Dict

from alpha_trader.owner import Owner
from alpha_trader.client import Client
from alpha_trader.logging import logger


class Miner(BaseModel):
    """
    Miner model

    Attributes:
        coins_per_hour: Number of coins that are mined per hour
        id: ID of the miner
        maximum_capacity: Maximum capacity of the miner, before transfer is needed
        next_level_coins_per_hour: Coins per hour of the miner on the next level
        next_level_costs: Costs of the next level of the miner
        owner: Owner of the miner
        storage: Storage of the miner
        transferable_coins: Transferable coins of the miner
        version: Version of the miner
        client: Client of the miner (for interaction with the API)
    """

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
            client=client,
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
        """
            Transfer coins from the miner to the clearing account
        Returns:
            API response
        """
        response = self.client.request("PUT", "api/v2/my/cointransfer")
        self.update_from_api_response(response.json())

        logger.info(
            f"Coins transferred. New transferable coins: {self.transferable_coins}"
        )

        return response.json()

    def upgrade(self) -> Dict:
        """
            Upgrade the miner to the next level.
        Returns:
            API response
        """
        response = self.client.request("PUT", "api/v2/my/minerupgrade")
        self.update_from_api_response(response.json())

        logger.info(f"Miner upgraded. New coins per hour: {self.coins_per_hour}")
        logger.info(f"Next level costs: {self.next_level_costs}")
        logger.info(f"Next level coins per hour: {self.next_level_coins_per_hour}")

        return response.json()

    def __get_coin_bid_price(self):
        """
            Get the coin bid price.
        Returns:
            Coin bid price
        """
        return self.client.get_price_spread("ACALPHCOIN").bid_price

    @property
    def next_level_amortization_hours(self) -> float:
        """
            Number of hours until the next level of the miner is amortized.
        Returns:
            Number of hours until the next level of the miner is amortized
        """
        coin_bid_price = self.__get_coin_bid_price()
        additional_earnings_per_hour = (
            self.next_level_coins_per_hour - self.coins_per_hour
        ) * coin_bid_price

        next_level_amortization_hours = (
            self.next_level_costs // additional_earnings_per_hour
        )

        logger.info(
            f"""Next level amortization hours: {
            next_level_amortization_hours
        } (or {
            next_level_amortization_hours / 24
        } days)"""
        )

        return next_level_amortization_hours

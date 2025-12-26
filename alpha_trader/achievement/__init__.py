from typing import Dict, Optional, Union
from pydantic import BaseModel

from alpha_trader.client import Client
from alpha_trader.logging import logger
from alpha_trader.exceptions import ResourceStateError


class Achievement(BaseModel):
    description: str
    type: str
    achievedDate: int
    claimed: bool
    coinReward: int
    endDate: Union[int, None]
    id: str
    version: int
    client: Client

    @staticmethod
    def initialize_from_api_response(api_response: Dict, client: Client):
        return Achievement(
            description=api_response["description"],
            type=api_response["type"],
            achievedDate=api_response["achievedDate"],
            claimed=api_response["claimed"],
            coinReward=api_response["coinReward"],
            endDate=api_response["endDate"],
            id=api_response["id"],
            version=api_response["version"],
            client=client,
        )

    def update_from_api_response(self, api_response: Dict):
        self.description = api_response["description"]
        self.type = api_response["type"]
        self.achievedDate = api_response["achievedDate"]
        self.claimed = api_response["claimed"]
        self.coinReward = api_response["coinReward"]
        self.endDate = api_response["endDate"]
        self.id = api_response["id"]
        self.version = api_response["version"]

    def __str__(self):
        return f"Achievement(description={self.description}, type={self.type}, achievedDate={self.achievedDate}, " \
               f"claimed={self.claimed}, coinReward={self.coinReward}, endDate={self.endDate}, id={self.id}, " \
               f"version={self.version}) "

    def __repr__(self):
        return self.__str__()

    def claim(self) -> None:
        """Claim this achievement.

        Raises:
            ResourceStateError: If the achievement has already been claimed
        """
        if self.claimed:
            raise ResourceStateError(
                f"Achievement '{self.description}' has already been claimed"
            )

        response = self.client.request(
            "PUT", f"api/v2/my/userachievementclaim/{self.id}"
        )

        self.update_from_api_response(response.json())

        logger.info(
            f'Achievement for "{self.description}" claimed. New claimed status: {self.claimed}'
        )

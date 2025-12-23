from typing import Dict, Optional
from pydantic import BaseModel, Field, ConfigDict

from alpha_trader.client import Client
from alpha_trader.logging import logger


class Achievement(BaseModel):
    """Achievement model representing a user achievement.

    Attributes:
        description: Description of the achievement
        type: Type of the achievement
        achieved_date: Timestamp when the achievement was achieved
        claimed: Whether the achievement has been claimed
        coin_reward: Number of coins rewarded for claiming
        end_date: End date of the achievement (if applicable)
        id: Unique identifier of the achievement
        version: Version number for optimistic locking
        client: API client for making requests
    """

    model_config = ConfigDict(populate_by_name=True)

    description: str
    type: str
    achieved_date: int = Field(alias="achievedDate")
    claimed: bool
    coin_reward: int = Field(alias="coinReward")
    end_date: Optional[int] = Field(default=None, alias="endDate")
    id: str
    version: int
    client: Client

    @staticmethod
    def initialize_from_api_response(api_response: Dict, client: Client) -> "Achievement":
        """Create an Achievement instance from an API response.

        Args:
            api_response: Dictionary containing the API response data
            client: API client instance

        Returns:
            Achievement instance
        """
        return Achievement(
            description=api_response["description"],
            type=api_response["type"],
            achieved_date=api_response["achievedDate"],
            claimed=api_response["claimed"],
            coin_reward=api_response["coinReward"],
            end_date=api_response["endDate"],
            id=api_response["id"],
            version=api_response["version"],
            client=client,
        )

    def update_from_api_response(self, api_response: Dict) -> None:
        """Update this instance from an API response.

        Args:
            api_response: Dictionary containing the API response data
        """
        self.description = api_response["description"]
        self.type = api_response["type"]
        self.achieved_date = api_response["achievedDate"]
        self.claimed = api_response["claimed"]
        self.coin_reward = api_response["coinReward"]
        self.end_date = api_response["endDate"]
        self.id = api_response["id"]
        self.version = api_response["version"]

    def __str__(self) -> str:
        return (
            f"Achievement(description={self.description}, type={self.type}, "
            f"achieved_date={self.achieved_date}, claimed={self.claimed}, "
            f"coin_reward={self.coin_reward}, end_date={self.end_date}, "
            f"id={self.id}, version={self.version})"
        )

    def __repr__(self) -> str:
        return self.__str__()

    def claim(self) -> None:
        """Claim this achievement.

        Raises:
            Exception: If the achievement has already been claimed
        """
        if self.claimed:
            raise Exception(f"Achievement '{self.description}' has already been claimed")

        response = self.client.request(
            "PUT", f"api/v2/my/userachievementclaim/{self.id}"
        )

        self.update_from_api_response(response.json())

        logger.info(
            f'Achievement for "{self.description}" claimed. New claimed status: {self.claimed}'
        )

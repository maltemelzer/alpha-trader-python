from pydantic import BaseModel
from typing import Dict, Union

from alpha_trader.partner import Partner
from alpha_trader.client import Client
from alpha_trader.achievement import Achievement
from alpha_trader.logging import logger
from alpha_trader.securities_account import SecuritiesAccount


class UserCapabilities(BaseModel):
    partner_id: str
    achievement_count: int
    achievement_total: int
    last_sponsoring_date: Union[None, str]
    level_2_user_end_date: Union[None, str]
    locale: str
    premium_end_date: Union[None, int]
    sponsored_hours: int
    team_department: Union[None, str]
    team_role: str
    team_role_description: Union[None, str]
    level_2_user: bool
    partner: bool
    premium: bool


class User(BaseModel):
    id: str
    username: str
    email: str
    jwt_token: str
    email_subscription_type: str
    capabilities: UserCapabilities
    gravatar_hash: str
    ref_id: str
    registration_date: int
    version: int
    my_user: bool
    client: Client

    @staticmethod
    def initialize_from_api_response(api_response: Dict, client: Client):
        return User(
            id=api_response["id"],
            username=api_response["username"],
            email=api_response["emailAddress"],
            jwt_token=api_response["jwtToken"],
            email_subscription_type=api_response["emailSubscriptionType"],
            capabilities=UserCapabilities(
                partner_id=api_response["userCapabilities"]["partnerId"],
                achievement_count=api_response["userCapabilities"]["achievementCount"],
                achievement_total=api_response["userCapabilities"]["achievementTotal"],
                last_sponsoring_date=api_response["userCapabilities"]["lastSponsoringDate"],
                level_2_user_end_date=api_response["userCapabilities"]["level2UserEndDate"],
                locale=api_response["userCapabilities"]["locale"],
                premium_end_date=api_response["userCapabilities"]["premiumEndDate"],
                sponsored_hours=api_response["userCapabilities"]["sponsoredHours"],
                team_department=api_response["userCapabilities"]["teamDepartment"],
                team_role=api_response["userCapabilities"]["teamRole"],
                team_role_description=api_response["userCapabilities"]["teamRoleDescription"],
                level_2_user=api_response["userCapabilities"]["level2User"],
                partner=api_response["userCapabilities"]["partner"],
                premium=api_response["userCapabilities"]["premium"]
            ),
            gravatar_hash=api_response["gravatarHash"],
            ref_id=api_response["refId"],
            registration_date=api_response["registrationDate"],
            version=api_response["version"],
            my_user=api_response["myUser"],
            client=client
        )

    @property
    def achievements(self):
        response = self.client.request("GET", f"api/v2/userachievements/{self.username}")

        logger.info("Retrieved achievements for user")

        return [Achievement.initialize_from_api_response(res, self.client) for res in response.json()]

    @property
    def securities_account(self):
        if not self.my_user:
            raise Exception("Cannot retrieve securities account for other users")

        response = self.client.request("GET", f"api/v2/my/securitiesaccount")

        return SecuritiesAccount.initialize_from_api_response(response.json(), self.client)



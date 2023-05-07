from __future__ import annotations

from pydantic import BaseModel
from typing import Dict, Union, List

from alpha_trader.client import Client
from alpha_trader.achievement import Achievement
from alpha_trader.logging import logger
from alpha_trader.securities_account import SecuritiesAccount
from alpha_trader.bank_account import BankAccount

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from alpha_trader.company import Company


class UserCapabilities(BaseModel):
    """
    User capabilities model

    Attributes:
        partner_id: Partner ID of the user
        achievement_count: Achievement count of the user
        achievement_total: Achievement total of the user
        last_sponsoring_date: Last sponsoring date of the user
        level_2_user_end_date: Level 2 user end date of the user
        locale: Locale of the user
        premium_end_date: Premium end date of the user
        sponsored_hours: Sponsored hours of the user
        team_department: Team department of the user
        team_role: Team role of the user
        team_role_description: Team role description of the user
        level_2_user: Level 2 user of the user
        partner: Flag if the user is a partner
        premium: Flag if the user is premium
    """

    partner_id: Union[str, None]
    achievement_count: Union[None, int]
    achievement_total: Union[None, int]
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
    """
    User model

    Attributes:
        id: ID of the user
        username: Username of the user
        email: Email of the user, only available for own user
        jwt_token: JWT token of the user, only available for own user
        email_subscription_type: Email subscription type of the user, only available for own user
        capabilities: Capabilities of the user
        gravatar_hash: Gravatar hash of the user
        ref_id: Ref ID of the user
        registration_date: Registration date of the user
        version: Version of the user
        my_user: Flag if the user is my user
        client: Client
    """

    id: str
    username: str
    email: Union[str, None]
    jwt_token: Union[str, None]
    email_subscription_type: Union[str, None]
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
            email=api_response.get("emailAddress", None),
            jwt_token=api_response.get("jwtToken", None),
            email_subscription_type=api_response.get("emailSubscriptionType", None),
            capabilities=UserCapabilities(
                partner_id=api_response["userCapabilities"].get("partnerId", None),
                achievement_count=api_response["userCapabilities"]["achievementCount"],
                achievement_total=api_response["userCapabilities"]["achievementTotal"],
                last_sponsoring_date=api_response["userCapabilities"][
                    "lastSponsoringDate"
                ],
                level_2_user_end_date=api_response["userCapabilities"][
                    "level2UserEndDate"
                ],
                locale=api_response["userCapabilities"]["locale"],
                premium_end_date=api_response["userCapabilities"]["premiumEndDate"],
                sponsored_hours=api_response["userCapabilities"]["sponsoredHours"],
                team_department=api_response["userCapabilities"]["teamDepartment"],
                team_role=api_response["userCapabilities"]["teamRole"],
                team_role_description=api_response["userCapabilities"][
                    "teamRoleDescription"
                ],
                level_2_user=api_response["userCapabilities"]["level2User"],
                partner=api_response["userCapabilities"]["partner"],
                premium=api_response["userCapabilities"]["premium"],
            ),
            gravatar_hash=api_response["gravatarHash"],
            ref_id=api_response["refId"],
            registration_date=api_response["registrationDate"],
            version=api_response["version"],
            my_user=api_response["myUser"],
            client=client,
        )

    @property
    def achievements(self) -> List[Achievement]:
        """
            Achievements of the user

        Returns:
            List of achievements
        """
        response = self.client.request(
            "GET", f"api/v2/userachievements/{self.username}"
        )

        logger.info("Retrieved achievements for user")

        return [
            Achievement.initialize_from_api_response(res, self.client)
            for res in response.json()
        ]

    @property
    def securities_account(self):
        """
            Get the securities account for the user

        Returns:
            Securities account
        """
        if not self.my_user:
            raise Exception("Cannot retrieve securities account for other users")

        response = self.client.request("GET", "api/v2/my/securitiesaccount")

        return SecuritiesAccount.initialize_from_api_response(
            response.json(), self.client
        )

    def found_company(
        self,
        company_name: str,
        cash_deposit: float,
        custom_number_of_shares: Union[int, None] = None,
        custom_asin: Union[str, None] = None,
    ) -> Company:
        """
            Found a company
        Args:
            company_name: Name of the company
            cash_deposit: Initial cash that should be deposited to the company
            custom_number_of_shares: Custom number of shares (premium feature)
            custom_asin: Custom ASIN (premium feature)

        Returns:
            Company
        """
        from alpha_trader.company import Company

        data = {
            "name": company_name,
            "cashDeposit": cash_deposit,
            "customNumberOfShares": custom_number_of_shares,
            "customAsin": custom_asin,
        }

        response = self.client.request("POST", "api/companies", data=data)

        return Company.initialize_from_api_response(response.json(), self.client)

    @property
    def companies(self) -> List[Company]:
        """
            Get all companies that the user is CEO of
        Returns:
            List of companies
        """
        from alpha_trader.company import Company

        response = self.client.request("GET", f"api/companies/ceo/userid/{self.id}")

        return [
            Company.initialize_from_api_response(res, self.client)
            for res in response.json()
        ]

    @property
    def salary(self) -> float:
        """
            Get the daily salary for the user
        Returns:
            Daily salary
        """
        response = self.client.request("GET", f"api/v2/possibledailysalary/{self.id}")

        return response.json()["value"]

    @property
    def bank_account(self) -> BankAccount:
        """
            Get the bank account for the user
        Returns:
            Bank account
        """
        if not self.my_user:
            raise Exception("Cannot retrieve bank account for other users")

        response = self.client.request("GET", "api/v2/my/bankaccounts/")

        return BankAccount.initialize_from_api_response(response.json()[0], self.client)

    def retrieve_salary(self) -> None:
        """
            Retrieve all the salaries for the user
        Returns:
            None

        """
        if not self.my_user:
            raise Exception("Cannot retrieve salary for other users.")

        response = self.client.request("PUT", "api/v2/my/salarypayments")

        if response.status_code == 200:
            logger.info("Successfully retrieved salary")

from __future__ import annotations

from pydantic import BaseModel
from typing import Dict

from alpha_trader.client import Client
from alpha_trader.listing import Listing
from alpha_trader.bank_account import BankAccount
from alpha_trader.user import User


class Company(BaseModel):
    achievement_count: int
    achievement_count: int
    bank_account: BankAccount
    ceo: User
    id: str
    listing: Listing
    logo_url: str
    name: str
    securities_account_id: str
    security_identifier: str
    version: int
    client: Client

    @staticmethod
    def initialize_from_api_response(api_response: Dict, client: Client):
        from alpha_trader.user import User

        return Company(
            achievement_count=api_response["achievementCount"],
            bank_account=BankAccount.initialize_from_api_response(
                api_response["bankAccount"], client=client
            ),
            ceo=User.initialize_from_api_response(api_response["ceo"], client),
            id=api_response["id"],
            listing=Listing.initialize_from_api_response(
                api_response["listing"], client
            ),
            logo_url=api_response["logoUrl"],
            name=api_response["name"],
            securities_account_id=api_response["securitiesAccountId"],
            security_identifier=api_response["securityIdentifier"],
            version=api_response["version"],
            client=client,
        )

    def update_from_api_response(self, api_response: Dict):
        self.achievement_count = api_response["achievementCount"]
        self.bank_account = BankAccount.initialize_from_api_response(
            api_response["bankAccount"]
        )
        self.ceo = User.initialize_from_api_response(api_response["ceo"], self.client)
        self.id = api_response["id"]
        self.listing = Listing.initialize_from_api_response(
            api_response["listing"], self.client
        )
        self.logo_url = api_response["logoUrl"]
        self.name = api_response["name"]
        self.securities_account_id = api_response["securitiesAccountId"]
        self.security_identifier = api_response["securityIdentifier"]
        self.version = api_response["version"]

    def __str__(self):
        return (
            f"Company(name={self.name}, security_identifier={self.security_identifier})"
        )

    def __repr__(self):
        return self.__str__()

    @property
    def securities_account(self):
        return self.client.get_securities_account(self.securities_account_id)

    def issue_bonds(
            self,
            face_value: float,
            interest_rate: float,
            maturity_date: int,
            number_of_bonds: int
    ):
        from alpha_trader.bonds import Bond

        return Bond.issue(
            self.id,
            face_value=face_value,
            interest_rate=interest_rate,
            maturity_date=maturity_date,
            number_of_bonds=number_of_bonds,
            client=self.client
        )

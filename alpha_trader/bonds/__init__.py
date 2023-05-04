from __future__ import annotations

from pydantic import BaseModel
from typing import Dict, TYPE_CHECKING, Union
import time

# if TYPE_CHECKING:
from alpha_trader.client import Client
from alpha_trader.listing import Listing
from alpha_trader.price.price_spread import PriceSpread
from alpha_trader.company import Company


class Issuer(BaseModel):
    id: str
    # listing: Listing
    name: str
    security_identifier: str
    version: int
    client: Client

    @staticmethod
    def initialize_from_api_response(api_response: Dict, client: Client) -> "Issuer":
        # from alpha_trader.listing import Listing

        return Issuer(
            id=api_response["id"],
            # listing=Listing.initialize_from_api_response(
            #     api_response["listing"], client
            # ),
            name=api_response["name"],
            security_identifier=api_response["securityIdentifier"],
            version=api_response["version"],
            client=client,
        )

    @property
    def company(self):
        response = self.client.request("GET", f"api/companies/securityIdentifier/{self.security_identifier}")

        return Company.initialize_from_api_response(response.json(), self.client)


class Bond(BaseModel):
    """
        Bond security.

        Attributes:
            face_value: Face value of the bond.
            id: ID of the bond.
            interest_rate: Interest rate of the bond.
            issue_date: Issue date of the bond.
            issuer: Issuer of the bond.
            listing: Listing of the bond.
            maturity_date: Maturity date of the bond.
            name: Name of the bond.
            price_spread: Price spread of the bond.
            repurchase_listing: Repurchase listing of the bond.
            version: Version of the bond.
            volume: Volume
            client: Client for interacting with the API.
    """
    face_value: int
    id: str
    interest_rate: int
    issue_date: int
    issuer: Issuer
    listing: Listing
    maturity_date: int
    name: str
    price_spread: Union[PriceSpread]
    repurchase_listing: Listing
    version: int
    volume: int
    client: Client

    @staticmethod
    def initialize_from_api_response(api_response: Dict, client: Client, price_spread: PriceSpread = None):
        from alpha_trader.listing import Listing
        from alpha_trader.price.price_spread import PriceSpread

        if api_response["priceSpread"] is not None:
            price_spread = PriceSpread.initialize_from_api_response(api_response["priceSpread"], client)

        return Bond(
            face_value=api_response["faceValue"],
            id=api_response["id"],
            interest_rate=api_response["interestRate"],
            issue_date=api_response["issueDate"],
            issuer=Issuer.initialize_from_api_response(api_response["issuer"], client=client),
            listing=Listing.initialize_from_api_response(api_response["listing"], client),
            maturity_date=api_response["maturityDate"],
            name=api_response["name"],
            price_spread=price_spread,
            repurchase_listing=Listing.initialize_from_api_response(api_response["repurchaseListing"], client),
            version=api_response["version"],
            volume=api_response["volume"],
            client=client
        )

    @staticmethod
    def issue(
        company_id: str,
        face_value: float,
        interest_rate: float,
        maturity_date: int,
        number_of_bonds: int,
        client: Client
    ) -> "Bond":
        """
            Issue new bonds
        Args:
            client: API Client
            company_id: ID of the company
            face_value: face value of the bond
            interest_rate: interest rate
            maturity_date: maturity date
            number_of_bonds: quantity of bonds to issue

        Returns:
            Bond
        """
        data = {
            "companyId": company_id,
            "faceValue": face_value,
            "interestRate": interest_rate,
            "maturityDate": maturity_date,
            "numberOfBonds": number_of_bonds
        }
        response = client.request("POST", "api/bonds", data=data)
        print(response.text)

        return Bond.initialize_from_api_response(response.json(), client)

    def __str__(self):
        return f"Bond(name={self.name}, volume={self.volume}, price_spread={self.price_spread}) "

    def __repr__(self):
        return self.__str__()

    @property
    def remaining_time(self) -> float:
        """
            Calculate remaining time
        Returns:
            remaining time
        """
        return self.listing.end_date - time.time() * 1000

    @property
    def effective_interest_rate(self) -> float:
        """
            Calculate effective interest rate
        Returns:
            effective interest rate
        """
        remaining_days = self.remaining_time / 60 / 60 / 24 / 1000
        effective_interest_rate = (100 - self.price_spread.ask_price + self.interest_rate) / remaining_days

        return effective_interest_rate

from __future__ import annotations

from pydantic import BaseModel
from typing import Dict, List, Optional, Any, TYPE_CHECKING

if TYPE_CHECKING:
    from alpha_trader.client import Client
    from alpha_trader.listing import Listing
    from alpha_trader.price.price_spread import PriceSpread


class SystemBond(BaseModel):
    """
    System bond (central bank bond).

    System bonds are issued by companies and bought by the central bank
    at the current main interest rate. They provide a way for companies
    to borrow money from the central bank.

    Attributes:
        id: Bond ID
        name: Bond name
        face_value: Face value per bond
        volume: Total volume of bonds
        interest_rate: Interest rate
        issue_date: Date of issue (timestamp)
        maturity_date: Maturity date (timestamp)
        security_identifier: Bond security identifier
        repurchase_security_identifier: Repurchase listing security identifier
        version: Entity version
    """
    id: str
    name: str
    face_value: float
    volume: float
    interest_rate: float
    issue_date: int
    maturity_date: int
    security_identifier: str
    repurchase_security_identifier: str
    version: int
    client: Optional[Any] = None

    model_config = {"arbitrary_types_allowed": True}

    @staticmethod
    def initialize_from_api_response(
        api_response: Dict, client: "Client" = None
    ) -> "SystemBond":
        listing = api_response.get("listing", {})
        repurchase_listing = api_response.get("repurchaseListing", {})

        return SystemBond(
            id=api_response.get("id", ""),
            name=api_response.get("name", ""),
            face_value=api_response.get("faceValue", 0.0),
            volume=api_response.get("volume", 0.0),
            interest_rate=api_response.get("interestRate", 0.0),
            issue_date=api_response.get("issueDate", 0),
            maturity_date=api_response.get("maturityDate", 0),
            security_identifier=listing.get("securityIdentifier", ""),
            repurchase_security_identifier=repurchase_listing.get("securityIdentifier", ""),
            version=api_response.get("version", 0),
            client=client,
        )

    @property
    def listing(self) -> "Listing":
        """Get the listing for this bond."""
        from alpha_trader.listing import Listing

        response = self.client.request(
            "GET", f"api/listings/{self.security_identifier}"
        )
        return Listing.initialize_from_api_response(response.json(), self.client)

    @property
    def repurchase_listing(self) -> "Listing":
        """Get the repurchase listing for this bond."""
        from alpha_trader.listing import Listing

        response = self.client.request(
            "GET", f"api/listings/{self.repurchase_security_identifier}"
        )
        return Listing.initialize_from_api_response(response.json(), self.client)

    @property
    def price_spread(self) -> "PriceSpread":
        """Get the price spread for this bond."""
        from alpha_trader.price.price_spread import PriceSpread

        response = self.client.request(
            "GET", f"api/pricespreads/{self.security_identifier}"
        )
        return PriceSpread.initialize_from_api_response(response.json(), self.client)

    def __str__(self):
        return (
            f"SystemBond({self.name}, volume={self.volume:.2f}, "
            f"interest_rate={self.interest_rate:.2%})"
        )

    def __repr__(self):
        return self.__str__()

    @staticmethod
    def issue(
        client: "Client",
        company_id: str,
        number_of_bonds: int,
    ) -> "SystemBond":
        """
        Issue new system bonds to be bought by the central bank.

        Args:
            client: API client
            company_id: ID of the company issuing the bonds
            number_of_bonds: Number of bonds to issue

        Returns:
            Created system bond
        """
        data = {
            "companyId": company_id,
            "numberOfBonds": number_of_bonds,
        }

        response = client.request("POST", "api/systembonds", data=data)
        return SystemBond.initialize_from_api_response(response.json(), client)


def get_system_bonds(client: "Client") -> List[SystemBond]:
    """
    Get all system bonds.

    Args:
        client: API client

    Returns:
        List of system bonds
    """
    response = client.request("GET", "api/systembonds")
    data = response.json()

    if isinstance(data, list):
        return [SystemBond.initialize_from_api_response(item, client) for item in data]
    return []


def get_system_bond(client: "Client", bond_id: str) -> SystemBond:
    """
    Get system bond by ID.

    Args:
        client: API client
        bond_id: Bond ID

    Returns:
        System bond details
    """
    response = client.request("GET", f"api/systembonds/{bond_id}")
    return SystemBond.initialize_from_api_response(response.json(), client)


def get_system_bond_by_security(
    client: "Client", security_identifier: str
) -> SystemBond:
    """
    Get system bond by security identifier.

    Args:
        client: API client
        security_identifier: Security identifier

    Returns:
        System bond details
    """
    response = client.request(
        "GET", f"api/systembonds/securityidentifier/{security_identifier}"
    )
    return SystemBond.initialize_from_api_response(response.json(), client)


def get_main_interest_rate(client: "Client") -> float:
    """
    Get the current main interest rate.

    Args:
        client: API client

    Returns:
        Current main interest rate
    """
    response = client.request("GET", "api/maininterestrate/latest/")
    data = response.json()
    return data.get("value", 0.0)


def get_average_bond_interest_rate(client: "Client") -> float:
    """
    Get the average bond interest rate.

    Args:
        client: API client

    Returns:
        Average bond interest rate
    """
    response = client.request("GET", "api/v2/averagebondinterestrate")
    data = response.json()
    return data.get("value", 0.0)

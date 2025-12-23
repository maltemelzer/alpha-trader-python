from __future__ import annotations

from pydantic import BaseModel
from typing import Dict, List, Optional, TYPE_CHECKING
from enum import Enum

if TYPE_CHECKING:
    from alpha_trader.client import Client
    from alpha_trader.listing import Listing
    from alpha_trader.company import Company


class WarrantType(str, Enum):
    """Warrant types."""
    CALL = "CALL"
    PUT = "PUT"


class Warrant(BaseModel):
    """
    Warrant (derivative instrument).

    Attributes:
        id: Warrant ID
        type: Warrant type (CALL or PUT)
        ratio: Conversion ratio
        subscription_period_date: Date until which warrant can be exercised
        underlying_value: Current value of the underlying
        underlying_cap_value: Cap value for the underlying
        security_identifier: Warrant security identifier
        underlying_security_identifier: Underlying security identifier
        company_id: Issuing company ID
        company_name: Issuing company name
        version: Entity version
    """
    id: str
    type: str
    ratio: float
    subscription_period_date: int
    underlying_value: float
    underlying_cap_value: float
    security_identifier: str
    underlying_security_identifier: str
    company_id: str
    company_name: str
    version: int
    client: Optional["Client"] = None

    model_config = {"arbitrary_types_allowed": True}

    @staticmethod
    def initialize_from_api_response(
        api_response: Dict, client: "Client" = None
    ) -> "Warrant":
        listing = api_response.get("listing", {})
        underlying = api_response.get("underlying", {})
        company = api_response.get("company", {})

        return Warrant(
            id=api_response.get("id", ""),
            type=api_response.get("type", ""),
            ratio=api_response.get("ratio", 0.0),
            subscription_period_date=api_response.get("subscriptionPeriodDate", 0),
            underlying_value=api_response.get("underlyingValue", 0.0),
            underlying_cap_value=api_response.get("underlyingCapValue", 0.0),
            security_identifier=listing.get("securityIdentifier", ""),
            underlying_security_identifier=underlying.get("securityIdentifier", ""),
            company_id=company.get("id", ""),
            company_name=company.get("name", ""),
            version=api_response.get("version", 0),
            client=client,
        )

    @property
    def listing(self) -> "Listing":
        """Get the listing for this warrant."""
        from alpha_trader.listing import Listing

        response = self.client.request(
            "GET", f"api/listings/{self.security_identifier}"
        )
        return Listing.initialize_from_api_response(response.json(), self.client)

    @property
    def underlying(self) -> "Listing":
        """Get the underlying listing."""
        from alpha_trader.listing import Listing

        response = self.client.request(
            "GET", f"api/listings/{self.underlying_security_identifier}"
        )
        return Listing.initialize_from_api_response(response.json(), self.client)

    @property
    def company(self) -> "Company":
        """Get the issuing company."""
        from alpha_trader.company import Company

        response = self.client.request(
            "GET", f"api/companies/{self.company_id}"
        )
        return Company.initialize_from_api_response(response.json(), self.client)

    @property
    def is_call(self) -> bool:
        """Check if this is a call warrant."""
        return self.type == WarrantType.CALL.value

    @property
    def is_put(self) -> bool:
        """Check if this is a put warrant."""
        return self.type == WarrantType.PUT.value

    def __str__(self):
        return (
            f"Warrant({self.security_identifier}, type={self.type}, "
            f"underlying={self.underlying_security_identifier})"
        )

    def __repr__(self):
        return self.__str__()

    @staticmethod
    def create(
        client: "Client",
        company_id: str,
        underlying_asin: str,
        warrant_type: WarrantType,
        cash_deposit: float,
    ) -> "Warrant":
        """
        Create a new warrant.

        Args:
            client: API client
            company_id: ID of the company issuing the warrant
            underlying_asin: Security identifier of the underlying
            warrant_type: Type of warrant (CALL or PUT)
            cash_deposit: Cash deposit for the warrant

        Returns:
            Created warrant
        """
        params = {
            "companyId": company_id,
            "underlyingAsin": underlying_asin,
            "type": warrant_type.value if isinstance(warrant_type, WarrantType) else warrant_type,
            "cashDeposit": cash_deposit,
        }

        response = client.request("POST", "api/v2/warrants", params=params)
        return Warrant.initialize_from_api_response(response.json(), client)


def get_warrants(
    client: "Client",
    underlying_asin: Optional[str] = None,
    page: int = 0,
    size: int = 20,
    sort: Optional[str] = None,
) -> List[Warrant]:
    """
    Get list of warrants.

    Args:
        client: API client
        underlying_asin: Optional filter by underlying security identifier
        page: Page number (0-indexed)
        size: Page size
        sort: Sort order

    Returns:
        List of warrants
    """
    params = {"page": page, "size": size}
    if underlying_asin:
        params["underlyingAsin"] = underlying_asin
    if sort:
        params["sort"] = sort

    response = client.request("GET", "api/v2/warrants", params=params)
    data = response.json()

    # Handle paginated response
    content = data.get("content", data) if isinstance(data, dict) else data
    if isinstance(content, list):
        return [Warrant.initialize_from_api_response(item, client) for item in content]
    return []


def get_warrant(client: "Client", warrant_id: str) -> Warrant:
    """
    Get warrant by ID.

    Args:
        client: API client
        warrant_id: Warrant ID

    Returns:
        Warrant details
    """
    response = client.request("GET", f"api/v2/warrants/{warrant_id}")
    return Warrant.initialize_from_api_response(response.json(), client)

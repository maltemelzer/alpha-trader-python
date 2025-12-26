from __future__ import annotations

from pydantic import BaseModel
from typing import Dict, List, Optional, Any, TYPE_CHECKING

if TYPE_CHECKING:
    from alpha_trader.client import Client
    from alpha_trader.listing import Listing


class IndexMember(BaseModel):
    """
    Index member (constituent).

    Attributes:
        security_identifier: Security identifier (ASIN)
        name: Security name
        weight: Weight in the index
    """
    security_identifier: str
    name: str
    weight: Optional[float]

    @staticmethod
    def initialize_from_api_response(api_response: Dict) -> "IndexMember":
        return IndexMember(
            security_identifier=api_response.get("securityIdentifier", ""),
            name=api_response.get("name", ""),
            weight=api_response.get("weight"),
        )


class CompactIndex(BaseModel):
    """
    Compact index view for listing.

    Attributes:
        id: Index ID
        name: Index name
        security_identifier: Index security identifier
        members_count: Number of members in the index
        owner_id: Owner user ID
        owner_username: Owner username
        version: Entity version
    """
    id: str
    name: str
    security_identifier: str
    members_count: int
    owner_id: str
    owner_username: str
    version: int

    @staticmethod
    def initialize_from_api_response(api_response: Dict) -> "CompactIndex":
        listing = api_response.get("listing", {})
        owner = api_response.get("owner", {})
        return CompactIndex(
            id=api_response.get("id", ""),
            name=api_response.get("name", ""),
            security_identifier=listing.get("securityIdentifier", ""),
            members_count=api_response.get("membersCount", 0),
            owner_id=owner.get("id", ""),
            owner_username=owner.get("username", ""),
            version=api_response.get("version", 0),
        )

    def __str__(self):
        return f"Index({self.name}, members={self.members_count})"

    def __repr__(self):
        return self.__str__()


class Index(BaseModel):
    """
    Full index view with members.

    Attributes:
        name: Index name
        base_value: Base value of the index
        chaining_factor: Chaining factor for index calculation
        next_chaining_date: Next date when chaining will occur
        members: List of index members
        owner_id: Owner user ID
        owner_username: Owner username
        security_identifier: Index security identifier
    """
    name: str
    base_value: float
    chaining_factor: float
    next_chaining_date: int
    members: List[IndexMember]
    owner_id: str
    owner_username: str
    security_identifier: str
    client: Optional[Any] = None

    model_config = {"arbitrary_types_allowed": True}

    @staticmethod
    def initialize_from_api_response(
        api_response: Dict, client: "Client" = None
    ) -> "Index":
        listing = api_response.get("listing", {})
        owner = api_response.get("owner", {})
        members_data = api_response.get("members", [])

        members = [IndexMember.initialize_from_api_response(m) for m in members_data]

        return Index(
            name=api_response.get("name", ""),
            base_value=api_response.get("baseValue", 0.0),
            chaining_factor=api_response.get("chainingFactor", 1.0),
            next_chaining_date=api_response.get("nextChainingDate", 0),
            members=members,
            owner_id=owner.get("id", ""),
            owner_username=owner.get("username", ""),
            security_identifier=listing.get("securityIdentifier", ""),
            client=client,
        )

    @property
    def listing(self) -> "Listing":
        """Get the listing for this index."""
        from alpha_trader.listing import Listing

        response = self.client.request(
            "GET", f"api/listings/{self.security_identifier}"
        )
        return Listing.initialize_from_api_response(response.json(), self.client)

    def __str__(self):
        return (
            f"Index({self.name}, base_value={self.base_value:.2f}, "
            f"members={len(self.members)})"
        )

    def __repr__(self):
        return self.__str__()


def get_indexes(
    client: "Client",
    page: int = 0,
    size: int = 20,
    sort: Optional[str] = None,
) -> List[CompactIndex]:
    """
    Get list of all indexes.

    Args:
        client: API client
        page: Page number (0-indexed)
        size: Page size
        sort: Sort order

    Returns:
        List of compact index views
    """
    params = {"page": page, "size": size}
    if sort:
        params["sort"] = sort

    response = client.request("GET", "api/v2/indexes", params=params)
    data = response.json()

    # Handle paginated response
    content = data.get("content", data) if isinstance(data, dict) else data
    if isinstance(content, list):
        return [CompactIndex.initialize_from_api_response(item) for item in content]
    return []


def get_index(client: "Client", security_identifier: str) -> Index:
    """
    Get detailed index information.

    Args:
        client: API client
        security_identifier: Index security identifier

    Returns:
        Full index with members
    """
    response = client.request("GET", f"api/v2/index/{security_identifier}")
    return Index.initialize_from_api_response(response.json(), client)

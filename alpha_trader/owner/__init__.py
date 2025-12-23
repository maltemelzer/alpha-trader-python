from pydantic import BaseModel
from typing import Dict


class Owner(BaseModel):
    """Owner model representing an account owner.

    Attributes:
        clearing_account_id: ID of the associated clearing account
        id: Unique identifier of the owner
        private_account: Whether this is a private account
        version: Version for optimistic locking
    """

    clearing_account_id: str
    id: str
    private_account: bool
    version: int

    @staticmethod
    def from_api_response(api_response: Dict) -> "Owner":
        """Create an Owner instance from an API response.

        Args:
            api_response: Dictionary containing the API response data

        Returns:
            Owner instance
        """
        return Owner(
            clearing_account_id=api_response["clearingAccountId"],
            id=api_response["id"],
            private_account=api_response["privateAccount"],
            version=api_response["version"],
        )

    # Alias for consistency with other models
    initialize_from_api_response = from_api_response

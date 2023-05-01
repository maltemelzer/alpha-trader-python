from pydantic import BaseModel
from typing import Dict


class Owner(BaseModel):
    clearing_account_id: str
    id: str
    private_account: bool
    version: int

    @staticmethod
    def from_api_response(api_response: Dict):
        return Owner(
            clearing_account_id=api_response["clearingAccountId"],
            id=api_response["id"],
            private_account=api_response["privateAccount"],
            version=api_response["version"],
        )

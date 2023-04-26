from pydantic import BaseModel
from typing import Dict

from alpha_trader.client import Client
from alpha_trader.portfolio import Portfolio


class SecuritiesAccount(BaseModel):
    clearing_account_id: str
    id: str
    private_account: bool
    version: int
    client: Client

    @staticmethod
    def initialize_from_api_response(api_response: Dict, client: Client):
        return SecuritiesAccount(
            clearing_account_id=api_response["clearingAccountId"],
            id=api_response["id"],
            private_account=api_response["privateAccount"],
            version=api_response["version"],
            client=client
        )

    def __str__(self):
        return f"SecuritiesAccount(id={self.id})"

    def __repr__(self):
        return self.__str__()

    @property
    def portfolio(self):
        response = self.client.request("GET", f"api/portfolios/{self.id}")

        return Portfolio.initialize_from_api_response(response.json(), self.client)

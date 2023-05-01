from pydantic import BaseModel
from typing import Dict, Union

from alpha_trader.client import Client


class Listing(BaseModel):
    end_date: Union[int, None]
    name: str
    security_identifier: str
    start_date: int
    type: str
    client: Client

    @staticmethod
    def initialize_from_api_response(api_response: Dict, client: Client):
        return Listing(
            end_date=api_response["endDate"],
            name=api_response["name"],
            security_identifier=api_response["securityIdentifier"],
            start_date=api_response["startDate"],
            type=api_response["type"],
            client=client,
        )

    def update_from_api_response(self, api_response: Dict):
        self.end_date = api_response["endDate"]
        self.name = api_response["name"]
        self.security_identifier = api_response["securityIdentifier"]
        self.start_date = api_response["startDate"]
        self.type = api_response["type"]

    def __str__(self):
        return f"Listing(name={self.name}, security_identifier={self.security_identifier}, type={self.type})"

    def __repr__(self):
        return self.__str__()

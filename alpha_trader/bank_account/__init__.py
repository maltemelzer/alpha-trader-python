from pydantic import BaseModel
from typing import Dict


class BankAccount(BaseModel):
    cash: int
    id: str
    version: int

    @staticmethod
    def initialize_from_api_response(api_response: Dict):
        return BankAccount(
            cash=api_response["cash"],
            id=api_response["id"],
            version=api_response["version"],
        )

    def __str__(self):
        return f"BankAccount(cash={self.cash}, id={self.id}, version={self.version})"

    def __repr__(self):
        return self.__str__()

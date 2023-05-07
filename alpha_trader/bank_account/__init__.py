from pydantic import BaseModel
from typing import Dict

from alpha_trader.client import Client


class BankAccount(BaseModel):
    cash: int
    id: str
    version: int
    client: Client

    @staticmethod
    def initialize_from_api_response(api_response: Dict, client: Client):
        return BankAccount(
            cash=api_response["cash"],
            id=api_response["id"],
            version=api_response["version"],
            client=client,
        )

    def __str__(self):
        return f"BankAccount(cash={self.cash}, id={self.id}, version={self.version})"

    def __repr__(self):
        return self.__str__()

    def cash_transfer(self, amount: int, receiver_bank_account_id: str):
        data = {
            "cashAmount": amount,
            "receiverBankAccountId": receiver_bank_account_id,
            "senderBankAccountId": self.id,
        }

        return self.client.request("PUT", f"api/v2/banktransfer/{self.id}", data=data)

from typing import Dict, List
from pydantic import BaseModel

from alpha_trader.cash_transfer_log import CashTransferLog
from alpha_trader.poll import Poll
from alpha_trader.employment import Employment
from alpha_trader.bank_account import BankAccount
from alpha_trader.user import User
from alpha_trader.client import Client


class UserProfile(BaseModel):
    bank_account: BankAccount
    cash_transfer_logs: List[CashTransferLog]
    employments: List[Employment]
    initiated_polls: List[Poll]
    locale: str
    polls: List[Poll]
    salary_payments: List[Dict]
    user: User
    username: str
    version: int

    @staticmethod
    def from_api(client: Client, username: str):
        response = client.request("GET", f"api/userprofiles/{username}")

        return UserProfile.initialize_from_api_response(response.json(), client)

    @staticmethod
    def initialize_from_api_response(api_response: Dict, client: Client):
        pass
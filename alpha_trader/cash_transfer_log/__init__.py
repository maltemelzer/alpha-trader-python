from pydantic import BaseModel
from typing import Dict, List


class Message(BaseModel):
    filledString: str
    message: str
    substitutions: List[str]

    @staticmethod
    def initialize_from_api_response(api_response: Dict):
        return Message(
            filledString=api_response["filledString"],
            message=api_response["message"],
            substitutions=api_response["substitutions"],
        )


class CashTransferLog(BaseModel):
    amount: float
    date: int
    id: str
    message: Message
    receiverBankAccount: str
    senderBankAccount: str
    version: int

    @staticmethod
    def initialize_from_api_response(api_response: Dict):
        return CashTransferLog(
            amount=api_response["amount"],
            date=api_response["date"],
            id=api_response["id"],
            message=Message.initialize_from_api_response(api_response["message"]),
            receiverBankAccount=api_response["receiverBankAccount"],
            senderBankAccount=api_response["senderBankAccount"],
            version=api_response["version"],
        )

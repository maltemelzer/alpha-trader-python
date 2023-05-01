from pydantic import BaseModel
from typing import Dict


class Price(BaseModel):
    value: int
    date: int

    @staticmethod
    def initialize_from_api_response(api_response: Dict):
        return Price(value=api_response["value"], date=api_response["date"])

    def __str__(self):
        return f"Price(value={self.value}, date={self.date})"

    def __repr__(self):
        return self.__str__()

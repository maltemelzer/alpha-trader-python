from pydantic import BaseModel
from alpha_trader.company import Company
from typing import Dict
from alpha_trader.client import Client


class Employment(BaseModel):
    company: Company
    daily_wage: float
    id: str
    pay_automatically: bool
    start_date: int
    version: int

    @staticmethod
    def initialize_from_api_response(api_response: Dict, client: Client):
        return Employment(
            company=Company.initialize_from_api_response(api_response["company"], client),
            daily_wage=api_response["dailyWage"],
            id=api_response["id"],
            pay_automatically=api_response["payAutomatically"],
            start_date=api_response["startDate"],
            version=api_response["version"],
        )
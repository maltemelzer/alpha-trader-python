from pydantic import BaseModel

from alpha_trader.company import Company
from alpha_trader.client import Client


class BankingLicense(BaseModel):
    id: str
    company_id: str
    start_date: int
    version: int

    @staticmethod
    def initialize_from_api_response(api_response: dict, client: Client):
        return BankingLicense(
            id=api_response["id"],
            company_id=api_response["company"]["id"],
            start_date=api_response["startDate"],
            version=api_response["version"]
        )

    def __str__(self):
        return f"BankingLicense(id={self.id})"

    def __repr__(self):
        return self.__str__()


class CentralBankReserves(BaseModel):
    banking_license: BankingLicense
    cash_holding: float
    coins_for_next_boost: int
    id: str
    interest_rate_boost: float
    max_central_bank_loans: float
    version: int

    @staticmethod
    def initialize_from_api_response(api_response: dict, client: Client):
        return CentralBankReserves(
            banking_license=BankingLicense.initialize_from_api_response(api_response["bankingLicense"], client),
            cash_holding=api_response["cashHolding"],
            coins_for_next_boost=api_response["coinsForNextBoost"],
            id=api_response["id"],
            interest_rate_boost=api_response["interestRateBoost"],
            max_central_bank_loans=api_response["maxCentralBankLoans"],
            version=api_response["version"]
        )

    def increase(self, amount: float):
        response = self.client.request("POST", f"api/centralbankreserves?companyId={self.banking_license.company_id}&cashAmount={amount}")

        if response.status_code != 200:
            raise Exception(response.json())

        if response.status_code == 200:
            self.cash_holding += amount

        return response

    def get_coins_needed_for_boost(self, multiplier: int = 200):
        return self.coins_for_next_boost * multiplier

    def boost(self, multiplier: int = 200):
        response = self.client.request("POST", f"api/v2/centralbankreserves/{self.id}?increaseInterestRateBoost=true&multiplier={multiplier}")

        if response.status_code != 200:
            raise Exception(response.json())

        return response

    def payment_information(self):
        response = self.client.request("GET", f"api/lastcentralbankreservespayment")

        return response.json()

    def __str__(self):
        return f"CentralBankReserves(id={self.id})"

    def __repr__(self):
        return self.__str__()

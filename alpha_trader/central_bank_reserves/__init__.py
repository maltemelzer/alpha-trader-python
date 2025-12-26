from typing import Any, Dict

from pydantic import BaseModel

from alpha_trader.company import Company
from alpha_trader.client import Client
from alpha_trader.exceptions import APIError, InsufficientFundsError
from alpha_trader.logging import logger


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
    client: Client
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
            client=client,
            banking_license=BankingLicense.initialize_from_api_response(api_response["bankingLicense"], client),
            cash_holding=api_response["cashHolding"],
            coins_for_next_boost=api_response["coinsForNextBoost"],
            id=api_response["id"],
            interest_rate_boost=api_response["interestRateBoost"],
            max_central_bank_loans=api_response["maxCentralBankLoans"],
            version=api_response["version"]
        )

    def increase(self, amount: float) -> None:
        """Increase central bank reserves.

        Args:
            amount: Amount to increase reserves by

        Raises:
            InsufficientFundsError: If insufficient funds available
            APIError: If the operation fails
        """
        response = self.client.request(
            "PUT",
            f"api/centralbankreserves?companyId={self.banking_license.company_id}&cashAmount={amount}",
            raise_for_status=False,
        )

        if response.status_code != 200:
            try:
                error_data = response.json()
                message = error_data.get("message", str(error_data))
            except ValueError:
                message = response.text

            if "insufficient" in message.lower():
                raise InsufficientFundsError(message)
            raise APIError(
                message,
                status_code=response.status_code,
                endpoint="api/centralbankreserves",
            )

        self.cash_holding += amount
        logger.info(f"Increased central bank reserves by {amount}. New holding: {self.cash_holding}")

    def get_coins_needed_for_boost(self, multiplier: int = 200) -> int:
        """Get the number of coins needed for a boost.

        Args:
            multiplier: Boost multiplier (default 200)

        Returns:
            Number of coins needed
        """
        return self.coins_for_next_boost * multiplier

    def boost(self, multiplier: int = 200) -> Dict[str, Any]:
        """Boost the interest rate.

        Args:
            multiplier: Boost multiplier (default 200)

        Returns:
            Response data from the API

        Raises:
            InsufficientFundsError: If insufficient coins available
            APIError: If the operation fails
        """
        response = self.client.request(
            "PUT",
            f"api/v2/centralbankreserves/{self.id}?increaseInterestRateBoost=true&multiplier={multiplier}",
            raise_for_status=False,
        )

        if response.status_code != 200:
            try:
                error_data = response.json()
                message = error_data.get("message", str(error_data))
            except ValueError:
                message = response.text

            if "insufficient" in message.lower() or "coins" in message.lower():
                raise InsufficientFundsError(message)
            raise APIError(
                message,
                status_code=response.status_code,
                endpoint=f"api/v2/centralbankreserves/{self.id}",
            )

        logger.info(f"Boosted interest rate with multiplier {multiplier}")
        return response.json()

    def payment_information(self) -> Dict[str, Any]:
        """Get payment information for central bank reserves.

        Returns:
            Payment information from the API
        """
        response = self.client.request("GET", "api/lastcentralbankreservespayment")

        return response.json()

    def __str__(self):
        return f"CentralBankReserves(id={self.id})"

    def __repr__(self):
        return self.__str__()

from pydantic import BaseModel
from typing import Dict, Union, List

from alpha_trader.portfolio.position import Position
from alpha_trader.client import Client


class Portfolio(BaseModel):
    """
    Portfolio model

    Attributes:
        cash: Cash of the portfolio
        committed_cash: Committed cash of the portfolio
        positions: Positions of the portfolio
        securities_account_id: Securities account ID of the portfolio
        client: Client of the portfolio (for interaction with the API)
    """

    cash: int
    committed_cash: int
    positions: Union[List[Position], None]
    securities_account_id: str
    client: Client

    @staticmethod
    def initialize_from_api_response(api_response: Dict, client: Client) -> "Portfolio":
        return Portfolio(
            cash=api_response["cash"],
            committed_cash=api_response["committedCash"],
            positions=[
                Position.initialize_from_api_response(res, client)
                for res in api_response["positions"]
            ],
            securities_account_id=api_response["securitiesAccountId"],
            client=client,
        )

    def __str__(self):
        return f"""Portfolio(securities_account_id={self.securities_account_id}, cash={self.cash}, \
        committed_cash={self.committed_cash}, positions={self.positions})"""

    def __repr__(self):
        return self.__str__()

    @property
    def uncommitted_cash(self) -> float:
        """
            Uncommitted cash of the portfolio
        Returns:
            Uncommitted cash
        """
        return self.cash - self.committed_cash

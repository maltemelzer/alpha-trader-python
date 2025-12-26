from __future__ import annotations

from pydantic import BaseModel
from typing import Dict, List, Optional, Union, TYPE_CHECKING
from enum import Enum

if TYPE_CHECKING:
    from alpha_trader.client import Client


class HighscoreType(str, Enum):
    """Available highscore types."""
    NETWORTH = "NETWORTH"
    BOOK_VALUE = "BOOK_VALUE"
    CASH = "CASH"
    SHARES = "SHARES"
    DAILY_PROFIT = "DAILY_PROFIT"
    WEEKLY_PROFIT = "WEEKLY_PROFIT"
    MONTHLY_PROFIT = "MONTHLY_PROFIT"


class UserHighscoreEntry(BaseModel):
    """
    User highscore entry.

    Attributes:
        user_id: User ID
        username: Username
        gravatar_hash: User's gravatar hash
        value: Current highscore value
        date: Date of the entry
        history_date: Historical date for comparison
        history_position: Historical position
        history_value: Historical value
    """
    user_id: str
    username: str
    gravatar_hash: str
    value: float
    date: str
    history_date: Optional[int]
    history_position: Optional[int]
    history_value: Optional[float]

    @staticmethod
    def initialize_from_api_response(api_response: Dict) -> "UserHighscoreEntry":
        user = api_response.get("user", {})
        return UserHighscoreEntry(
            user_id=user.get("id", ""),
            username=user.get("username", ""),
            gravatar_hash=user.get("gravatarHash", ""),
            value=api_response.get("value", 0.0),
            date=api_response.get("date", ""),
            history_date=api_response.get("historyDate"),
            history_position=api_response.get("historyPosition"),
            history_value=api_response.get("historyValue"),
        )

    def __str__(self):
        return f"UserHighscoreEntry({self.username}, value={self.value:.2f})"

    def __repr__(self):
        return self.__str__()


class CompanyHighscoreEntry(BaseModel):
    """
    Company highscore entry.

    Attributes:
        company_id: Company ID
        company_name: Company name
        security_identifier: Security identifier (ASIN)
        value: Current highscore value
        date: Date of the entry
        history_date: Historical date for comparison
        history_position: Historical position
        history_value: Historical value
    """
    company_id: str
    company_name: str
    security_identifier: str
    value: float
    date: str
    history_date: Optional[int]
    history_position: Optional[int]
    history_value: Optional[float]

    @staticmethod
    def initialize_from_api_response(api_response: Dict) -> "CompanyHighscoreEntry":
        company = api_response.get("company", {})
        return CompanyHighscoreEntry(
            company_id=company.get("id", ""),
            company_name=company.get("name", ""),
            security_identifier=company.get("securityIdentifier", ""),
            value=api_response.get("value", 0.0),
            date=api_response.get("date", ""),
            history_date=api_response.get("historyDate"),
            history_position=api_response.get("historyPosition"),
            history_value=api_response.get("historyValue"),
        )

    def __str__(self):
        return f"CompanyHighscoreEntry({self.company_name}, value={self.value:.2f})"

    def __repr__(self):
        return self.__str__()


class AllianceHighscoreEntry(BaseModel):
    """
    Alliance highscore entry.

    Attributes:
        alliance_id: Alliance ID
        alliance_name: Alliance name
        value: Current highscore value
        date: Date of the entry
    """
    alliance_id: str
    alliance_name: str
    value: float
    date: str

    @staticmethod
    def initialize_from_api_response(api_response: Dict) -> "AllianceHighscoreEntry":
        alliance = api_response.get("alliance", {})
        return AllianceHighscoreEntry(
            alliance_id=alliance.get("id", ""),
            alliance_name=alliance.get("name", ""),
            value=api_response.get("value", 0.0),
            date=api_response.get("date", ""),
        )

    def __str__(self):
        return f"AllianceHighscoreEntry({self.alliance_name}, value={self.value:.2f})"

    def __repr__(self):
        return self.__str__()


def get_user_highscores(
    client: "Client",
    highscore_type: Union[HighscoreType, str] = HighscoreType.NETWORTH,
    page: int = 0,
    size: int = 20,
    sort: Optional[str] = None,
) -> List[UserHighscoreEntry]:
    """
    Get user highscore leaderboard.

    Args:
        client: API client
        highscore_type: Type of highscore to retrieve
        page: Page number (0-indexed)
        size: Page size
        sort: Sort order

    Returns:
        List of user highscore entries
    """
    if isinstance(highscore_type, HighscoreType):
        highscore_type = highscore_type.value

    params = {"highscoreType": highscore_type, "page": page, "size": size}
    if sort:
        params["sort"] = sort

    response = client.request("GET", "api/v2/userhighscores", params=params)
    data = response.json()

    # Handle paginated response
    content = data.get("content", data) if isinstance(data, dict) else data
    if isinstance(content, list):
        return [UserHighscoreEntry.initialize_from_api_response(item) for item in content]
    return []


def get_company_highscores(
    client: "Client",
    highscore_type: Union[HighscoreType, str] = HighscoreType.BOOK_VALUE,
    page: int = 0,
    size: int = 20,
    sort: Optional[str] = None,
) -> List[CompanyHighscoreEntry]:
    """
    Get company highscore leaderboard.

    Args:
        client: API client
        highscore_type: Type of highscore to retrieve
        page: Page number (0-indexed)
        size: Page size
        sort: Sort order

    Returns:
        List of company highscore entries
    """
    if isinstance(highscore_type, HighscoreType):
        highscore_type = highscore_type.value

    params = {"highscoreType": highscore_type, "page": page, "size": size}
    if sort:
        params["sort"] = sort

    response = client.request("GET", "api/v2/companyhighscores", params=params)
    data = response.json()

    # Handle paginated response
    content = data.get("content", data) if isinstance(data, dict) else data
    if isinstance(content, list):
        return [CompanyHighscoreEntry.initialize_from_api_response(item) for item in content]
    return []


def get_alliance_highscores(
    client: "Client",
    page: int = 0,
    size: int = 20,
    sort: Optional[str] = None,
) -> List[AllianceHighscoreEntry]:
    """
    Get alliance highscore leaderboard.

    Args:
        client: API client
        page: Page number (0-indexed)
        size: Page size
        sort: Sort order

    Returns:
        List of alliance highscore entries
    """
    params = {"page": page, "size": size}
    if sort:
        params["sort"] = sort

    response = client.request("GET", "api/v2/alliancehighscores", params=params)
    data = response.json()

    # Handle paginated response
    content = data.get("content", data) if isinstance(data, dict) else data
    if isinstance(content, list):
        return [AllianceHighscoreEntry.initialize_from_api_response(item) for item in content]
    return []


def get_best_users(
    client: "Client",
    page: int = 0,
    size: int = 20,
) -> List[UserHighscoreEntry]:
    """
    Get best users (top performers).

    Args:
        client: API client
        page: Page number (0-indexed)
        size: Page size

    Returns:
        List of top user entries
    """
    params = {"page": page, "size": size}
    response = client.request("GET", "api/v2/bestusers", params=params)
    data = response.json()

    content = data.get("content", data) if isinstance(data, dict) else data
    if isinstance(content, list):
        return [UserHighscoreEntry.initialize_from_api_response(item) for item in content]
    return []


def get_best_companies(
    client: "Client",
    page: int = 0,
    size: int = 20,
) -> List[CompanyHighscoreEntry]:
    """
    Get best companies (top performers).

    Args:
        client: API client
        page: Page number (0-indexed)
        size: Page size

    Returns:
        List of top company entries
    """
    params = {"page": page, "size": size}
    response = client.request("GET", "api/v2/bestcompanies", params=params)
    data = response.json()

    content = data.get("content", data) if isinstance(data, dict) else data
    if isinstance(content, list):
        return [CompanyHighscoreEntry.initialize_from_api_response(item) for item in content]
    return []

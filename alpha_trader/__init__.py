__version__ = "0.6.3"

# Core
from alpha_trader.client import Client

# Exceptions
from alpha_trader.exceptions import (
    AlphaTraderError,
    AuthenticationError,
    NotAuthenticatedError,
    APIError,
    NotFoundError,
    ValidationError,
    PermissionError,
    InsufficientFundsError,
    OrderError,
    ResourceStateError,
)

# New modules
from alpha_trader.trade_stats import TradeStats, TradeSummary, Trade
from alpha_trader.order_log import OrderLogEntry, get_order_logs, get_order_logs_by_security
from alpha_trader.highscore import (
    HighscoreType,
    UserHighscoreEntry,
    CompanyHighscoreEntry,
    AllianceHighscoreEntry,
    get_user_highscores,
    get_company_highscores,
    get_alliance_highscores,
    get_best_users,
    get_best_companies,
)
from alpha_trader.index import Index, CompactIndex, IndexMember, get_indexes, get_index
from alpha_trader.warrant import Warrant, WarrantType, get_warrants, get_warrant
from alpha_trader.historical_data import (
    HistorizedCompanyData,
    HistorizedListingData,
    get_company_history,
    get_listing_history,
)
from alpha_trader.notification import (
    Notification,
    get_notifications,
    get_unread_count,
    mark_all_as_read,
    delete_all_notifications,
)
from alpha_trader.system_bond import (
    SystemBond,
    get_system_bonds,
    get_system_bond,
    get_system_bond_by_security,
    get_main_interest_rate,
    get_average_bond_interest_rate,
)

__all__ = [
    # Version
    "__version__",
    # Core
    "Client",
    # Exceptions
    "AlphaTraderError",
    "AuthenticationError",
    "NotAuthenticatedError",
    "APIError",
    "NotFoundError",
    "ValidationError",
    "PermissionError",
    "InsufficientFundsError",
    "OrderError",
    "ResourceStateError",
    # Trade Statistics
    "TradeStats",
    "TradeSummary",
    "Trade",
    # Order Logs
    "OrderLogEntry",
    "get_order_logs",
    "get_order_logs_by_security",
    # Highscores
    "HighscoreType",
    "UserHighscoreEntry",
    "CompanyHighscoreEntry",
    "AllianceHighscoreEntry",
    "get_user_highscores",
    "get_company_highscores",
    "get_alliance_highscores",
    "get_best_users",
    "get_best_companies",
    # Indexes
    "Index",
    "CompactIndex",
    "IndexMember",
    "get_indexes",
    "get_index",
    # Warrants
    "Warrant",
    "WarrantType",
    "get_warrants",
    "get_warrant",
    # Historical Data
    "HistorizedCompanyData",
    "HistorizedListingData",
    "get_company_history",
    "get_listing_history",
    # Notifications
    "Notification",
    "get_notifications",
    "get_unread_count",
    "mark_all_as_read",
    "delete_all_notifications",
    # System Bonds
    "SystemBond",
    "get_system_bonds",
    "get_system_bond",
    "get_system_bond_by_security",
    "get_main_interest_rate",
    "get_average_bond_interest_rate",
]

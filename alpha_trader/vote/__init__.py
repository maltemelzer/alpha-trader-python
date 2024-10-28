from pydantic import BaseModel
from alpha_trader.user import User


class Vote(BaseModel):
    type: str
    voices: int
    voter: User

from alpha_trader.client import Client
import os


def test_user_initialization():
    client = Client(
        base_url=os.getenv("BASE_URL"),
        username=os.getenv("USERNAME"),
        password=os.getenv("PASSWORD"),
        partner_id=os.getenv("PARTNER_ID"),
    )

    client.login()
    user = client.get_user()

    assert user.id is not None
    assert user.username == os.getenv("USERNAME")
    assert user.email is not None
    assert user.jwt_token is not None


def test_achievements():
    client = Client(
        base_url=os.getenv("BASE_URL"),
        username=os.getenv("USERNAME"),
        password=os.getenv("PASSWORD"),
        partner_id=os.getenv("PARTNER_ID"),
    )

    client.login()
    user = client.get_user()

    assert user.achievements is not None
    assert user.achievements[0].claimed is False


def test_securities_account():
    client = Client(
        base_url=os.getenv("BASE_URL"),
        username=os.getenv("USERNAME"),
        password=os.getenv("PASSWORD"),
        partner_id=os.getenv("PARTNER_ID"),
    )

    client.login()
    user = client.get_user()

    assert user.securities_account is not None
    assert user.securities_account.private_account
    assert user.securities_account.id is not None
    assert user.securities_account.clearing_account_id is not None

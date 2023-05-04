from alpha_trader.client import Client
import os


def test_login():
    client = Client(
        base_url=os.getenv("BASE_URL"),
        username=os.getenv("USERNAME"),
        password=os.getenv("PASSWORD"),
        partner_id=os.getenv("PARTNER_ID"),
    )

    client.login()

    assert client.authenticated is True
    assert client.token is not None


def test_get_user():
    client = Client(
        base_url=os.getenv("BASE_URL"),
        username=os.getenv("USERNAME"),
        password=os.getenv("PASSWORD"),
        partner_id=os.getenv("PARTNER_ID"),
    )

    client.login()

    user = client.get_user()

    assert user.id is not None
    assert user.username is not None
    assert user.email is not None
    assert user.jwt_token is not None


def test_get_miner():
    client = Client(
        base_url=os.getenv("BASE_URL"),
        username=os.getenv("USERNAME"),
        password=os.getenv("PASSWORD"),
        partner_id=os.getenv("PARTNER_ID"),
    )

    client.login()

    miner = client.get_miner()

    assert miner.id is not None
    assert miner.coins_per_hour == 0
    assert miner.transferable_coins == 1


def test_get_listing():
    client = Client(
        base_url=os.getenv("BASE_URL"),
        username=os.getenv("USERNAME"),
        password=os.getenv("PASSWORD"),
        partner_id=os.getenv("PARTNER_ID"),
    )

    client.login()

    listing = client.get_listing("ACALPHCOIN")

    assert listing.end_date is None
    assert listing.name == "AlphaCoins"
    assert listing.security_identifier == "ACALPHCOIN"
    assert listing.type == "COIN"


def test_get_price_spread():
    client = Client(
        base_url=os.getenv("BASE_URL"),
        username=os.getenv("USERNAME"),
        password=os.getenv("PASSWORD"),
        partner_id=os.getenv("PARTNER_ID"),
    )

    client.login()

    price_spread = client.get_price_spread("ACALPHCOIN")

    assert price_spread.security_identifier == "ACALPHCOIN"
    assert price_spread.listing.security_identifier == "ACALPHCOIN"
    assert price_spread.last_price is not None


def test_get_securities_account():
    client = Client(
        base_url=os.getenv("BASE_URL"),
        username=os.getenv("USERNAME"),
        password=os.getenv("PASSWORD"),
        partner_id=os.getenv("PARTNER_ID"),
    )

    client.login()

    user = client.get_user()

    securities_account = client.get_securities_account(user.securities_account.id)

    assert securities_account.id == user.securities_account.id
    assert securities_account.private_account



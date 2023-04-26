import os

from alpha_trader.client import Client


if __name__ == "__main__":
    client = Client(
        base_url=os.getenv("BASE_URL"),
        username=os.getenv("USERNAME"),
        password=os.getenv("PASSWORD"),
        partner_id=os.getenv("PARTNER_ID")
    )

    client.login()

    user = client.get_user()
    miner = client.get_miner()
    miner.transfer_coins()
    coin_price = client.get_price_spread("ACALPHCOIN")

    # if miner.next_level_amortization_hours < 720:
    #     miner.upgrade()

    print("Done")

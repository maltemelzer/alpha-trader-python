import os
import time

from alpha_trader.client import Client


if __name__ == "__main__":
    client_main_account = Client(
        base_url=os.getenv("BASE_URL"),
        username=os.getenv("USERNAME"),
        password=os.getenv("PASSWORD"),
        partner_id=os.getenv("PARTNER_ID"),
    )
    client_main_account.login()

    client_secondary_account = Client(
        base_url=os.getenv("BASE_URL"),
        username=os.getenv("USERNAME_2"),
        password=os.getenv("PASSWORD_2"),
        partner_id=os.getenv("PARTNER_ID"),
    )
    client_secondary_account.login()

    user_main = client_main_account.get_user()
    user_secondary = client_secondary_account.get_user()

    response = user_main.bank_account.cash_transfer(amount=1000, receiver_bank_account_id=user_secondary.bank_account.id)

    print("Done")

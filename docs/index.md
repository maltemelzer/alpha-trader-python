# Welcome to the Python SDK for Alpha-Trader

The user interface can be reached at [https://alpha-trader.com](https://alpha-trader.com)

# Getting Started

## Installation

You can install the package via pip by cloning the repository and running

    pip install ./alpha_trader

## Authentication

To use the Python SDK you have to authenticate with a user and a partner id.
A partner id can be requested by contacting "km" in the Alpha-Trader user interface.

Now you can create a client:

    from alpha_trader.client import Client

    client = Client(username="MY_USERNAME", password="MY_PASSWORD", partner_id="MY_PARTNER_ID")

## Examples

### Get your user information

    client = Client(username="MY_USERNAME", password="MY_PASSWORD", partner_id="MY_PARTNER_ID")
    user = client.get_user()
    print(user)

### Transfer all coins from the miner

    miner = client.get_miner()
    miner.transfer_coins()

### Miner Upgrade

Check how many hours it takes before amortization of the next miner upgrade:

    miner = client.get_miner()
    miner.next_level_amortization_hours

Upgrade the miner if amortization is less then 7 days:

    if miner.next_level_amortization_hours < 24 * 7:
        miner.upgrade()
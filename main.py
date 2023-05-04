import os
import time

from alpha_trader.client import Client


if __name__ == "__main__":
    client = Client(
        base_url=os.getenv("BASE_URL"),
        username=os.getenv("USERNAME"),
        password=os.getenv("PASSWORD"),
        partner_id=os.getenv("PARTNER_ID"),
    )

    client.login()

    user = client.get_user()
    miner = client.get_miner()
    miner.transfer_coins()
    coin_price = client.get_price_spread("ACALPHCOIN")

    filter_definition = {
        "name": "Bond Filter",
        "listingFilter": {
            "nextFilters": [
                {
                    "operator": "AND",
                    "predicate": {
                        "field": "endDate",
                        "operator": "LESS_THAN",
                        "parameter": str(int(time.time() * 24*60*60)*1000)
                    },
                    "nextFilters": []
                }
            ],
            "operator": "WHERE",
            "predicate": {
                "field": "type",
                "operator": "EQUAL",
                "parameter": "BOND"
            },
        },
        "spreadFilter": {
            "nextFilters": [],
            "operator": "WHERE",
            "predicate": {
                "field": "askSize",
                "operator": "GREATER_THAN",
                "parameter": "0"
            }
        }
    }

    bonds = client.filter_listings(filter_definition=filter_definition)
    bond = client.get_bond(bonds[0].listing.security_identifier, price_spread=bonds[0])

    for b in bonds:
        bond = client.get_bond(b.listing.security_identifier, price_spread=b)
        print(bond.listing.security_identifier, bond.name, bond.effective_interest_rate)
    # if miner.next_level_amortization_hours < 720:
    #     miner.upgrade()

    print("Done")

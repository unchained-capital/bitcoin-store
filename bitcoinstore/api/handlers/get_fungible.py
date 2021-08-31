"""
Handles retrival of a fungible item by sku.
"""

import uuid
from bitcoinstore.extensions import db
from bitcoinstore.api.models.FungibleItem import FungibleItem

def get_fungible(sku) -> dict:

    try:
        item = db.session.query(FungibleItem).get(sku)

        if not item:
            return "FungibleItem: SKU does not exist"

        return item.get_summary()

    except Exception as e:
        print(e)
        return {}

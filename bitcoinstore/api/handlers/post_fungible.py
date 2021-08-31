"""
Handles the validation, sku creation, and loading of a fungible item to the db.
"""

import uuid
from bitcoinstore.extensions import db
from bitcoinstore.api.models.FungibleItem import FungibleItem

def post_fungible(properties) -> dict:

    try:
        sku = str( uuid.uuid4() )
        item = FungibleItem(sku, properties)

        db.session.add(item)
        db.session.commit()

        return item.get_summary()

    except Exception as e:
        print(e)
        return {}

"""
Handles the validation and loading of a fungible item to the db.
"""

from bitcoinstore.extensions import db
from bitcoinstore.api.models.FungibleItem import FungibleItem

def put_fungible(sku, properties) -> dict:

    try:
        item = db.session.query(FungibleItem).get(sku)

        if not item: # Insert new
            item = FungibleItem(sku, properties)
        else:
            item.update(properties)

        db.session.add(item)
        db.session.commit()

        return item.get_summary()

    except Exception as e:
        print(e)
        return {}

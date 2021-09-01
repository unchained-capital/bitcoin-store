"""
Handles the validation and adding or removing of item quantity by sku.
"""

import uuid
from bitcoinstore.extensions import db
from bitcoinstore.api.models.FungibleItem import FungibleItem

def post_fungible_add_remove(sku, quantity) -> dict:

    try:
        if not quantity or type(quantity) is not int:
            return "Must provide a valid quantity", 400

        item = db.session.query(FungibleItem).get(sku)

        if not item:
            return "Item with SKU does not exist", 404

        new_quantity = quantity + item.get_amount_in_stock()

        if new_quantity < 0:
            return "Can't adjust quantity below 0", 400

        item.set_amount_in_stock(new_quantity)

        db.session.add(item)
        db.session.commit()

        return item.get_summary()

    except Exception as e:
        print(e)
        return {}

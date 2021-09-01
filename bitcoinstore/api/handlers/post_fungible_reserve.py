"""
Reserve quantity of a fungible item for later sale to the user.
"""

from flask import session
from bitcoinstore.extensions import db
from bitcoinstore.api.models.FungibleItem import FungibleItem
from bitcoinstore.api.models.FungibleItemReservation import FungibleItemReservation

def post_fungible_reserve(sku, quantity) -> dict:

    try:
        if quantity < 1:
            return "FungibleItemReservation: Minimum 1 reserve quantity", 405

        item = db.session.query(FungibleItem).get(sku)

        if not item:
            return "FungibleItemReservation: SKU does not exist", 404

        amount_available = item.get_amount_in_stock() - item.get_reserved_quantity()

        if amount_available < quantity:
            return "FungibleItemReservation: Can't reserve more than available", 405

        reservation = FungibleItemReservation(sku, quantity)

        db.session.add(reservation)
        db.session.commit()

        return item.get_summary()

    except Exception as e:
        print(e)
        return {}

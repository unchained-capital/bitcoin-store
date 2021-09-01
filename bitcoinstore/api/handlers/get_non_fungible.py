"""
Handles retrival of a non-fungible item by sku and sn.
"""

from bitcoinstore.extensions import db
from bitcoinstore.api.models.NonFungibleItem import NonFungibleItem
from bitcoinstore.api.models.NonFungibleType import NonFungibleType

def get_non_fungible(sku, sn) -> dict:

    try:
        type = db.session.query(NonFungibleType).get(sku)

        if not type:
            return "NonFungibleType: SKU does not exist", 404


        item = db.session.query(NonFungibleItem).get(sn)

        if not item:
            return "NonFungibleItem: SN does not exist", 404

        item_summary = item.get_summary()
        type_summary = type.get_summary()

        return {
            "sn": item_summary['sn'],
            "color": item_summary['color'],
            "description": type_summary['description'],
            "notes": item_summary['notes'],
            "price_cents": item_summary['price_cents'],
            "shipping_weight_grams": type_summary['shipping_weight_grams'],
            "sku": item_summary['sku'],
            "sold": item_summary['sold']
        }

    except Exception as e:
        print(e)
        return {}

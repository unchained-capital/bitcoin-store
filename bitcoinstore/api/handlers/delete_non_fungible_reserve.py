"""
Reserves a non-fungible item for sale.
"""

from bitcoinstore.extensions import db
from bitcoinstore.api.models.NonFungibleItem import NonFungibleItem
from bitcoinstore.api.models.NonFungibleType import NonFungibleType

def delete_non_fungible_reserve(sku, sn) -> dict:

    try:
        type = db.session.query(NonFungibleType).get(sku)

        if not type:
            print("Here 1")
            return "NonFungibleType: SKU does not exist", 404


        item = db.session.query(NonFungibleItem).get(sn)

        if not item:
            print("Here 2")
            return "NonFungibleItem: SN does not exist", 404

        if item.get_sold() is True:
            return "Item is already sold", 405
        else:
            item.set_reserved(False)

        db.session.add(item)
        db.session.commit()

        item_summary = item.get_summary()
        type_summary = type.get_summary()

        return {
            "sn": item_summary['sn'],
            "color": item_summary['color'],
            "description": type_summary['description'],
            "notes": item_summary['notes'],
            "price_cents": item_summary['price_cents'],
            "reserved": item_summary['reserved'],
            "shipping_weight_grams": type_summary['shipping_weight_grams'],
            "sku": item_summary['sku'],
            "sold": item_summary['sold']
        }

    except Exception as e:
        print(e)
        return {}

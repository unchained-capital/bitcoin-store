"""
Handles the validation and loading of a non-fungible item and its associated
parent type to the db.
"""

from bitcoinstore.extensions import db
from bitcoinstore.api.models.NonFungibleItem import NonFungibleItem
from bitcoinstore.api.models.NonFungibleType import NonFungibleType

def put_non_fungible(sku, sn, properties) -> dict:

    try:
        type = db.session.query(NonFungibleType).get(sku)

        if not type: # SKU type does not exist, create one
            type = NonFungibleType(sku, properties)
            db.session.add(type)
        else:
            type.update(properties)


        item = db.session.query(NonFungibleItem).get(sn)
        
        if not item: # SN item does not exist, create one
            item = NonFungibleItem(sn, properties)
            item.sku = sku
        else:
            item.update(properties)


        db.session.add(type)
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

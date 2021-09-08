
class FungibleItem:
    """
    A class object to hold contents of a row of fungible_inventory database.
    This is the object returned from the DAO, and to clients of the InventoryService.
    """
    def __init__(self, sku = '', name = '', description = '', price_cents = 0, shipping_weight = 0, quantity = 0):
        self.sku = sku
        self.name = name
        self.description = description
        self.price_cents = price_cents
        self.shipping_weight = shipping_weight
        self.quantity = quantity


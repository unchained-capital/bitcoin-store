
class NonFungibleItem:
    """
    A class object to hold contents of a row of non_fungible_inventory database.
    This is the object returned from the DAO, and to clients of the InventoryService.
    """

    def __init__(self, sku = '', serial_number = '', name = '', description = '', unique_description = '',
                 price_cents = 0, shipping_weight = 0, is_available = False):
        self.sku = sku
        self.serial_number = serial_number
        self.name = name
        self.description = description
        self.unique_description = unique_description
        self.price_cents = price_cents
        self.shipping_weight = shipping_weight
        self.is_available = is_available

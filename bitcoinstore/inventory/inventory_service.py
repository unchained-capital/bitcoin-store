from bitcoinstore.inventory.inventory_dao import FungibleInventoryDao, NonFungibleInventoryDao
from threading import Lock
from bitcoinstore.inventory.exceptions import *


class InventoryService:
    """
    Implementation for the Inventory Service.
    This is to be called by the main browser frontend, Cart Service, Reservation Timeout Serivce, and backend inventory
    management service.

    Note that this service is NOT aware of how the reservation system works. Whenever an item is added to a cart, that
    essentially removes an inventory item from this service. And when item is removed from cart, manually or via a
    timeout system, the item is added back to the inventory via this service. The difference between reserved items, vs
    fulfilled items is maintained by the Reservation Service, outside of Inventory Service.

    Note that Inventory Service is not directly handling client requests, so it doesn't handle authorization for the
    user context. It is assumed higher level services will do those checks.

    This class is thread safe.
    """

    # (TODO): The locks below are not granular currently. Ideally replace them by named resource locks, which can
    # lock on a unique key like SKU or serial. This way, a thread will only lock the DB rows that it needs to touch.
    _fungible_lock = Lock()
    _non__fungible_lock = Lock()

    def __init__(self):
        self._fungible_dao = FungibleInventoryDao()
        self._non_fungible_dao = NonFungibleInventoryDao()

    def list_fungible_items(self):
        """
        Returns list of all fungible items.
        Doesn't require acquiring a lock.
        """
        return self._fungible_dao.list_items()

    def get_fungible_item(self, sku):
        """
        Returns a particular fungible item identified by the sku nmme.
        Doesn't require acquiring a lock.
        """
        return self._fungible_dao.get_item(sku)

    def remove_fungible_item(self, sku, count):
        """
        Removes few items from a particular fungible item identified by the sku nmme.
        Returns errors if item doesn't exist or short of inventory.

        Note that if removal of items reduced invetory size to 0, this DOES NOT delete the item from inventory.

        It requires acquiring a lock, since we are adjusting inventory quantity over 2 different db calls.
        """

        self._fungible_lock.acquire()
        item = self.get_fungible_item(sku)
        if item is None:
            self._fungible_lock.release()
            raise ItemNotFoundException()
        if item.quantity < count:
            self._fungible_lock.release()
            raise InsufficientInventoryException()
        new_count = item.quantity - count
        self._fungible_dao.update_item_count(sku, new_count)
        self._fungible_lock.release()

    def add_fungible_item(self, sku, count):
        """
        Adds a few items(count) to a particular fungible item identified by the sku nmme.
        Returns errors if the inventory item doesn't exist.

        It requires acquiring a lock, since we are adjusting inventory quantity over 2 different db calls.
        """
        self._fungible_lock.acquire()
        item = self.get_fungible_item(sku)
        if item is None:
            self._fungible_lock.release()
            raise ItemNotFoundException()
        new_count = item.quantity + count
        self._fungible_dao.update_item_count(sku, new_count)
        self._fungible_lock.release()

    def create_new_fungible_item(self, fungible_item):
        """
        Creates a new fungible item.
        Returns error if the inventory item already exist.

        It requires acquiring a lock, since we want only the winning thread in a race condition to return success. The
        losing thread in the race condition will get an error, indicating its version failed to apply.
        """
        self._fungible_lock.acquire()
        item = self.get_fungible_item(fungible_item.sku)
        if item is not None:
            self._fungible_lock.release()
            raise AlreadyExistingInventoryException()
        self._fungible_dao.create_item(fungible_item)
        self._fungible_lock.release()

    def delete_fungible_item(self, sku):
        """
        Deletes a fungible item, identified by the sku.
        Throws error if item didn't exist.

        Doesn't require a lock.
        """
        item = self.get_fungible_item(sku)
        if item is None:
            raise ItemNotFoundException()
        self._fungible_dao.delete_item(sku)

    """
    All methods below are for non-fungible inventory, and implemented similarly to the fungible inventory, except for
    minor details on the quantity vs is_available columns.
    The documentation for below methods should be almost same as for above methods for fungible inventory.
    """

    def list_non_fungible_items(self):
        return self._non_fungible_dao.list_items()

    def get_non_fungible_item(self, sku, serial):
        return self._non_fungible_dao.get_item(sku, serial)

    def remove_non_fungible_item(self, sku, serial):
        self._non_fungible_lock.acquire()
        item = self.get_non_fungible_item(sku, serial)
        if item is None:
            self._fungible_lock.release()
            raise ItemNotFoundException()
        if not item.is_available:
            self._fungible_lock.release()
            raise InsufficientInventoryException()
        self._non_fungible_dao.update_item_availability(sku, serial, False)
        self._non_fungible_lock.release()

    def add_non_fungible_item(self, sku, serial):
        self._non_fungible_lock.acquire()
        item = self.get_non_fungible_item(sku, serial)
        if item is None:
            self._fungible_lock.release()
            raise ItemNotFoundException()
        if item.is_available:
            self._fungible_lock.release()
            raise AlreadyExistingInventoryException()
        self._non_fungible_dao.update_item_availability(sku, serial, True)
        self._non_fungible_lock.release()

    def create_new_non_fungible_item(self, non_fungible_item):
        self._non_fungible_lock.acquire()
        item = self.get_non_fungible_item(non_fungible_item.sku, non_fungible_item.serial)
        if item is not None:
            self._fungible_lock.release()
            raise AlreadyExistingInventoryException()
        self._non_fungible_dao.create_item(non_fungible_item)
        self._non_fungible_lock.release()

    def delete_non_fungible_item(self, sku, serial):
        item = self.get_non_fungible_item(sku, serial)
        if item is None:
            raise ItemNotFoundException()
        self._non_fungible_dao.delete_item(sku, serial)

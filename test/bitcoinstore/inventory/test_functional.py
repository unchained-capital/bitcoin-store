
import pytest

from bitcoinstore.inventory.exceptions import ItemNotFoundException, InsufficientInventoryException, \
    AlreadyExistingInventoryException
from bitcoinstore.inventory.fungible_item import FungibleItem
from bitcoinstore.inventory.inventory_dao import FungibleInventoryDao
from bitcoinstore.inventory.inventory_service import InventoryService

class TestFunctionalInventoryService():

    @pytest.fixture(autouse=True)
    def setup(self):
        self.service = InventoryService()

    def test_list_fungible_items(self):
        items = self.service.list_fungible_items()
        assert len(items) == 3
        for item in items:
            assert item.sku is not None

    def test_get_fungible_item(self):
        sku = 'A'
        item = self.service.get_fungible_item(sku)

        # (TODO) Finish the test, and other functional tests.

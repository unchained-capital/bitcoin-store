from unittest import mock
from unittest.mock import MagicMock

import pytest

from bitcoinstore.inventory.exceptions import ItemNotFoundException, InsufficientInventoryException, \
    AlreadyExistingInventoryException
from bitcoinstore.inventory.fungible_item import FungibleItem
from bitcoinstore.inventory.inventory_dao import FungibleInventoryDao
from bitcoinstore.inventory.inventory_service import InventoryService


class TestInventoryService():

    @pytest.fixture(autouse=True)
    def setup(self):
        self.service = InventoryService()

    @mock.patch.object(FungibleInventoryDao, 'list_items')
    def test_list_fungible_items(self, mock_list_items):
        self.service.list_fungible_items()

        mock_list_items.assert_called_once()

    @mock.patch.object(FungibleInventoryDao, 'get_item')
    def test_get_fungible_item(self, mock_get_item):
        sku = "Test Sku"

        self.service.get_fungible_item(sku)

        mock_get_item.assert_called_once_with(sku)

    @mock.patch.object(FungibleInventoryDao, 'get_item', return_value=None)
    @mock.patch.object(FungibleInventoryDao, 'update_item_count')
    def test_remove_fungible_item_non_existent_item(self, mock_update_item_count, mock_get_item):
        sku = "Test Sku"

        try:
            self.service.remove_fungible_item(sku, 5)
        except ItemNotFoundException:
            pass

        mock_get_item.assert_called_once_with(sku)
        mock_update_item_count.assert_not_called()

    @mock.patch.object(FungibleInventoryDao, 'get_item', return_value=FungibleItem(quantity = 3))
    @mock.patch.object(FungibleInventoryDao, 'update_item_count')
    def test_remove_fungible_item_insufficient_inventory(self, mock_update_item_count, mock_get_item):
        sku = "Test Sku"

        try:
            self.service.remove_fungible_item(sku, 5)
        except InsufficientInventoryException:
            pass

        mock_get_item.assert_called_once_with(sku)
        mock_update_item_count.assert_not_called()

    @mock.patch.object(FungibleInventoryDao, 'get_item', return_value=FungibleItem(quantity = 3))
    @mock.patch.object(FungibleInventoryDao, 'update_item_count')
    def test_remove_fungible_item_success(self, mock_update_item_count, mock_get_item):
        sku = "Test Sku"

        self.service.remove_fungible_item(sku, 3)

        mock_get_item.assert_called_once_with(sku)
        mock_update_item_count.assert_called_once_with(sku, 0)

    @mock.patch.object(FungibleInventoryDao, 'get_item', return_value=FungibleItem(sku='A'))
    @mock.patch.object(FungibleInventoryDao, 'create_item')
    def test_create_new_fungible_item_failure(self, mock_create_item, mock_get_item):
        sku = "A"

        try:
            self.service.create_new_fungible_item(FungibleItem(sku=sku))
        except AlreadyExistingInventoryException:
            pass

        mock_get_item.assert_called_once_with(sku)
        mock_create_item.assert_not_called()

    @mock.patch.object(FungibleInventoryDao, 'get_item', return_value=None)
    @mock.patch.object(FungibleInventoryDao, 'create_item')
    def test_create_new_fungible_item_success(self, mock_create_item, mock_get_item):
        sku = 'A'
        item = FungibleItem(sku=sku)

        self.service.create_new_fungible_item(item)

        mock_get_item.assert_called_once_with(sku)
        mock_create_item.assert_called_once_with(item)

"""
(TODO): Finish all tests for non fungible items too
"""

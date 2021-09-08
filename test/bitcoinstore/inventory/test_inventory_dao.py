from unittest import mock
from unittest.mock import MagicMock

import pytest

from bitcoinstore.inventory.exceptions import ItemNotFoundException, InsufficientInventoryException, \
    AlreadyExistingInventoryException
from bitcoinstore.inventory.fungible_item import FungibleItem
from bitcoinstore.inventory.inventory_dao import FungibleInventoryDao
from bitcoinstore.inventory.inventory_service import InventoryService


class TestInventoryService():
    """
    (TODO): Write unit-tests
    """
    pass

from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, Boolean, text

from bitcoinstore.inventory.fungible_item import FungibleItem
from bitcoinstore.inventory.non_fungible_item import NonFungibleItem

engine = create_engine("sqlite+pysqlite:///:memory:", echo=True, future=True)
meta = MetaData()

fungible_inventory = Table(
    'fungible_inventory', meta,
    Column('sku', String, primary_key=True),
    Column('name', String),
    Column('description', String),
    Column('price', Integer),
    Column('shipping_weight', Integer),
    Column('quantity', Integer)
)

non_fungible_inventory = Table(
    'non_fungible_inventory', meta,
    Column('sku', String, primary_key=True),
    Column('serial', String, primary_key=True),
    Column('name', String),
    Column('description', String),
    Column('unique_description', String),
    Column('price', Integer),
    Column('shipping_weight', Integer),
    Column('is_available', Boolean)
)

"""
*
*
*
For the purpose of testing, below will create the tables, and insert some static rows.
*
*
*
"""

meta.create_all(engine)

with engine.begin() as conn:
    conn.execute(
        fungible_inventory.insert(), [
            {'sku': 'A', 'name': 'name of A', 'description': 'Description of A',
             'price': 300, 'shipping_weight': '142', 'quantity': 5},
            {'sku': 'B', 'name': 'name of B', 'description': 'Description of B',
             'price': 400, 'shipping_weight': '152', 'quantity': 8},
            {'sku': 'C', 'name': 'name of C', 'description': 'Description of C',
             'price': 100, 'shipping_weight': '12', 'quantity': 0}
        ]
    )
    conn.execute(
        non_fungible_inventory.insert(), [
            {'sku': 'D', 'serial': 'D1', 'name': 'name of D', 'description': 'Description of D',
             'unique_description': 'D1 of D', 'price': 300, 'shipping_weight': '142', 'is_available': True},
            {'sku': 'E', 'serial': 'E1', 'name': 'name of E', 'description': 'Description of E',
             'unique_description': 'E1 of E', 'price': 330, 'shipping_weight': '13', 'is_available': False}
        ]
    )


class FungibleInventoryDao:
    """
    DAO for the table fungible_inventory
    """

    def __init__(self):
        self._conn = engine.connect()

    def list_items(self):
        ex = fungible_inventory.select()
        rows = self._conn.execute(ex)
        items = []
        for row in rows:
            sku, name, description, price, shipping_weight, quantity = row
            item = FungibleItem(sku, name, description, price, shipping_weight, quantity)
            items.append(item)
        return items

    def get_item(self, sku):
        t = text("SELECT * FROM non_fungible_inventory WHERE SKU = :sku")
        rows = self._conn.execute(t, {"sku": sku}).fetchall()
        assert (len(rows) < 2), "Multiple items for given SKU!"
        if len(rows) == 0:
            return None
        sku, name, description, price, shipping_weight, quantity = rows[0]
        return FungibleItem(sku, name, description, price, shipping_weight, quantity)

    def update_item_count(self, sku, count):
        t = text("UPDATE fungible_inventory SET quantity = :count WHERE SKU = :sku")
        self._conn.execute(t, count=count, sku=sku)

    def create_item(self, fungible_item):
        t = text("INSERT INTO fungible_inventory (sku, name, description, price, shipping_weight, quantity) "
                 "VALUES (:sku, :name, :desc, :price, shipping_wt, :qty)")
        self._conn.execute(t, sku=fungible_item.sku, name=fungible_item.name, desc=fungible_item.description,
                           price=fungible_item.price, shipping_wt=fungible_item.shipping_weight,
                           qty=fungible_item.quantity)

    def delete_item(self, sku):
        t = text("DELETE FROM fungible_inventory WHERE SKU = :sku")
        self._conn.execute(t, sku=sku)


class NonFungibleInventoryDao:
    """
    DAO for the table non_fungible_inventory
    """

    def __init__(self):
        self._conn = engine.connect()

    def list_items(self):
        query = non_fungible_inventory.select()
        rows = self._conn.execute(query)
        items = []
        for row in rows:
            sku, serial, name, description, unique_description, price, shipping_weight, is_available = row
            item = NonFungibleItem(sku, serial, name, description, unique_description, price, shipping_weight,
                                   is_available)
            items.append(item)
        return items

    def get_item(self, sku, serial):
        t = text("select * from non_fungible_inventory where SKU = :sku and serial = :serial")
        rows = self._conn.execute(t, sku=sku, serial=serial).fetchall()
        assert (len(rows) < 2), "Multiple items for given SKU and Serial number!"
        if len(rows) == 0:
            return None
        sku, serial, name, description, unique_description, price, shipping_weight, is_available = rows[0]
        return FungibleItem(sku, serial, name, description, unique_description, price, shipping_weight, is_available)

    def update_item_availability(self, sku, serial, is_available):
        t = text("update non_fungible_inventory set is_available = :availability where SKU = :sku and serial = :serial")
        self._conn.execute(t, availability=is_available, sku=sku, serial=serial)

    def create_item(self, non_fungible_item):
        t = text("INSERT INTO non_fungible_inventory (sku, serial, name, description, unique_description, price, "
                 "shipping_weight, quantity) VALUES (:sku, :serial, :name, :desc, :unique_desc, :price, shipping_wt, "
                 ":qty)")
        self._conn.execute(t, sku=non_fungible_item.sku, serial=non_fungible_item.serial_number,
                           name=non_fungible_item.name, desc=non_fungible_item.description,
                           unique_desc=non_fungible_item.unique_description, price=non_fungible_item.price,
                           shipping_wt=non_fungible_item.shipping_weight, qty=non_fungible_item.quantity)

    def delete_item(self, sku, serial):
        t = text("DELETE FROM non_fungible_inventory WHERE SKU = :sku and serial = :serial")
        self._conn.execute(t, sku=sku, serial=serial)

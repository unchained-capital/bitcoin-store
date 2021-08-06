from dataclasses import dataclass
from bitcoinstore.extensions import db


"""
Prudcts can be bulk stock, and/or individual items.
Both stock and items are the same notional product,
but follow different relationship restrictions.

Stock is a fungible item, which can be interchanged with
other identital items, such as when ordering a new retail item.
Any item can fullfil the order, as long as its the same SKU.

Item is a non-fungible item, which is unqiue and can't be
interchanged with another item, such as used items.
Only the speicific item listed for sale can fullfil the order.
"""


@dataclass
class ProductStock(db.Model):
    id: int
    product_id: int
    color: str
    price: float
    currency: str
    quantity: int
    reserved: int

    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(
        db.Integer, db.ForeignKey("product.id"), nullable=False, unique=True
    )
    product = db.relationship("Product", back_populates="stock", uselist=False)
    color = db.Column(db.String)
    price = db.Column(db.Float)
    currency = db.Column(db.String(3))
    quantity = db.Column(db.Integer)
    reserved = db.Column(db.Integer)


@dataclass
class ProductItem(db.Model):
    id: int
    product_id: int
    color: str
    serial_number: str
    notes: str
    price: float
    currency: str
    is_reserved: bool

    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(
        db.Integer, db.ForeignKey("product.id"), nullable=False
    )
    product = db.relationship("Product", back_populates="items")
    color = db.Column(db.String)
    serial_number = db.Column(db.String)
    notes = db.Column(db.String())
    price = db.Column(db.Float)
    currency = db.Column(db.String(3))
    is_reserved = db.Column(db.Boolean, default=False)


@dataclass
class Product(db.Model):
    id: int
    sku: str
    name: str
    description: str
    weight: float
    stock: ProductStock
    items: list[ProductItem]

    id = db.Column(db.Integer, primary_key=True)
    sku = db.Column(db.String(12), nullable=False)
    name = db.Column(db.String, nullable=False)
    description = db.Column(db.String())
    weight = db.Column(db.Float)
    stock = db.relationship(
        "ProductStock", back_populates="product", uselist=False
    )
    items = db.relationship("ProductItem", back_populates="product")

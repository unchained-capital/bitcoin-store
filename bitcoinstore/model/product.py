from dataclasses import dataclass

from bitcoinstore.extensions import db


@dataclass
class NonFungibleProduct(db.Model):
    id: int
    productId: int
    serial: str
    nfpDesc: str
    reserved: bool

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    productId = db.Column(
        db.Integer, db.ForeignKey("product.id"), nullable=False
    )
    product = db.relationship("Product", back_populates="nonFungible", uselist=False)
    serial = db.Column(db.String(36), unique=True, nullable=False)
    nfpDesc = db.Column(db.String(100))
    reserved = db.Column(db.Boolean, default=False)

@dataclass
class FungibleProduct(db.Model):
    productId: int
    qty: int
    qtyReserved: int = 0

    productId = db.Column(
        db.Integer, db.ForeignKey("product.id"), primary_key=True, nullable=False
    )
    product = db.relationship("Product", back_populates="fungible")
    qty = db.Column(db.Integer, nullable=False)
    qtyReserved = db.Column(db.Integer, nullable=False)

@dataclass
class Product(db.Model):
    id: int
    sku: str
    name: str
    description: str
    price: int
    weight: int
    fungible: list[FungibleProduct]
    nonFungible: NonFungibleProduct

    id = db.Column(db.Integer, primary_key = True, autoincrement=True)
    sku = db.Column(db.String, unique = True, nullable = False)
    name = db.Column(db.String(20))
    description = db.Column(db.String(100))
    # denominated in pennies
    price = db.Column(db.Integer)
    # ounces? grams? definitely grams if we're selling illegal fungibles
    weight = db.Column(db.Integer)
    nonFungible = db.relationship(
        "NonFungibleProduct", back_populates="product", uselist=False
    )
    fungible = db.relationship("FungibleProduct", back_populates="product")
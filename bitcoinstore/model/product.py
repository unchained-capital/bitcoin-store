from dataclasses import dataclass

from bitcoinstore.extensions import db


@dataclass
class NonFungibleProduct(db.Model):
    id: int
    productId: int
    serial: str
    nfp_desc: str
    reserved: bool
    price: int
    weight: float

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    productId = db.Column(
        db.Integer, db.ForeignKey("product.id"), nullable=False
    )
    product = db.relationship(
        "Product", back_populates="nonFungible", uselist=False
    )
    serial = db.Column(db.String(36), unique=True, nullable=False)
    nfp_desc = db.Column(db.String(100))
    reserved = db.Column(db.Boolean, default=False)
    # denominated in pennies
    price = db.Column(db.Integer)
    # pounds? kilograms? definitely kilos if we're selling illegal fungibles
    weight = db.Column(db.Float)

    db.Index("index_serial", unique=True)

    def serialize(self):
        return {
            "id": self.product.id,
            "sku": self.product.sku,
            "name": self.product.name,
            "description": self.product.description,
            "fungible": False,
            "serial": self.serial,
            "nfp_desc": self.nfp_desc,
            "reserved": self.reserved,
            "price": self.price,
            "weight": self.weight
        }

@dataclass
class FungibleProduct(db.Model):
    productId: int
    qty: int
    qty_reserved: int
    price: int
    weight: float

    productId = db.Column(
        db.Integer, db.ForeignKey("product.id"), primary_key=True, nullable=False
    )
    product = db.relationship("Product", back_populates="fungible")
    qty = db.Column(db.Integer, default=0)
    qty_reserved = db.Column(db.Integer, default=0)
    # denominated in pennies
    price = db.Column(db.Integer)
    weight = db.Column(db.Float)

    db.CheckConstraint("qty >= qty_reserved")

    def serialize(self):
        return {
            "sku": self.product.sku,
            "name": self.product.name,
            "description": self.product.description,
            "fungible": True,
            "qty": self.qty,
            "qty_reserved": self.qty_reserved,
            "price": self.price,
            "weight": self.weight
        }

@dataclass
class Product(db.Model):
    id: int
    sku: str
    name: str
    description: str

    id = db.Column(db.Integer, primary_key = True, autoincrement=True)
    sku = db.Column(db.String, unique = True, nullable = False)
    name = db.Column(db.String(20))
    description = db.Column(db.String(100))
    nonFungible = db.relationship(
        "NonFungibleProduct", back_populates="product", uselist=False
    )
    fungible = db.relationship(
        "FungibleProduct", back_populates="product", uselist=False
    )

    db.Index("index_sku", unique=True)

    def serialize(self):
        repr = {
            "id": self.id,
            "sku": self.sku,
            "name": self.name,
            "description": self.description,
        }

        if self.nonFungible:
            repr.update({
                "fungible": False,
                "serial": self.nonFungible.serial,
                "nfp_desc": self.nonFungible.nfp_desc,
                "reserved": self.nonFungible.reserved,
                "price": self.nonFungible.price,
                "weight": self.nonFungible.weight
            })
        else:
            repr.update({
                "fungible": True,
                "qty": self.fungible.qty,
                "qty_reserved": self.fungible.qty_reserved,
                "price": self.fungible.price,
                "weight": self.fungible.weight
            })

        return repr
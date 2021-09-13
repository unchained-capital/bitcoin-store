from dataclasses import dataclass

from bitcoinstore.extensions import db


@dataclass
class NonFungibleSku(db.Model):
    sku: str
    name: str
    description: str

    sku = db.Column(db.String, primary_key=True, nullable=False)
    name = db.Column(db.String(20))
    description = db.Column(db.String(100))


@dataclass
class NonFungibleProduct(db.Model):
    id: int
    sku: str
    nonFungibleSku: NonFungibleSku
    serial: str
    reserved: bool
    nfp_desc: str
    price: int
    weight: float

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    sku = db.Column(
        db.String, db.ForeignKey("non_fungible_sku.sku"), nullable=False
    )
    nonFungibleSku = db.relationship("NonFungibleSku")
    serial = db.Column(db.String(36), unique=True, nullable=False)
    reserved = db.Column(db.Boolean, default=False)
    nfp_desc = db.Column(db.String(100))
    # denominated in pennies
    price = db.Column(db.Integer)
    # pounds? kilograms? definitely kilos if we're selling illegal fungibles
    weight = db.Column(db.Float)

    db.Index("index_serial", unique=True)
    db.Index("index_sku")

    def serialize(self):
        return {
            "non_fungible_id": self.id,
            "sku": self.sku,
            "name": self.nonFungibleSku.name,
            "description": self.nonFungibleSku.description,
            "fungible": False,
            "serial": self.serial,
            "reserved": self.reserved,
            "nfp_desc": self.nfp_desc,
            "price": self.price,
            "weight": self.weight,
        }


@dataclass
class FungibleProduct(db.Model):
    id: int
    sku: str
    name: str
    description: str
    qty: int
    qty_reserved: int
    price: int
    weight: float

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    sku = db.Column(db.String, unique=True, nullable=False)
    name = db.Column(db.String(20))
    description = db.Column(db.String(100))
    qty = db.Column(db.Integer, default=0)
    qty_reserved = db.Column(db.Integer, default=0)
    # denominated in pennies
    price = db.Column(db.Integer)
    weight = db.Column(db.Float)

    # TODO why doesn't this constraint work?
    db.CheckConstraint("qty >= qty_reserved")
    db.Index("index_sku", unique=True)

    def serialize(self):
        return {
            "fungible_id": self.id,
            "sku": self.sku,
            "name": self.name,
            "description": self.description,
            "fungible": True,
            "qty": self.qty,
            "qty_reserved": self.qty_reserved,
            "price": self.price,
            "weight": self.weight,
        }

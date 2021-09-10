from dataclasses import dataclass
from datetime import datetime

from sqlalchemy import DateTime, func

from bitcoinstore.extensions import db
from bitcoinstore.model.product import FungibleProduct, NonFungibleProduct


@dataclass
class NonFungibleReservation(db.Model):
    id: int
    serial: str
    nonFungibleProduct: NonFungibleProduct
    userId: str
    created: datetime
    expiration: datetime
    expired: bool

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    serial = db.Column(db.String, db.ForeignKey("non_fungible_product.serial"), nullable=False)
    nonFungibleProduct = db.relationship("NonFungibleProduct")
    userId = db.Column(db.String, nullable = False)
    created = db.Column(DateTime(timezone=True), server_default=func.now())
    expiration = db.Column(DateTime(timezone=True))
    expired = db.Column(db.Boolean, default=False)

    db.Index("expiration", unique=True)
    db.Index("serial")
    db.Index("userId")

    def serialize(self):
        return {
            "id": self.id,
            "fungible": False,
            "serial": self.serial,
            "userId": self.userId,
            "created": self.created.isoformat(),
            "expiration": self.expiration.isoformat(),
            "expired": self.expired,
        }

@dataclass
class FungibleReservation(db.Model):
    id: int
    sku: str
    fungibleProduct: FungibleProduct
    qty: int
    userId: str
    created: datetime
    expiration: datetime
    expired: bool

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    sku = db.Column(db.String, db.ForeignKey("fungible_product.sku"), nullable=False)
    fungibleProduct = db.relationship("FungibleProduct")
    qty = db.Column(db.Integer)
    userId = db.Column(db.String, nullable = False)
    created = db.Column(DateTime(timezone=True), server_default=func.now())
    expiration = db.Column(DateTime(timezone=True))
    expired = db.Column(db.Boolean, default=False)

    db.Index("expiration", unique=True)
    db.Index("sku")
    db.Index("userId")

    def serialize(self):
        return {
            "id": self.id,
            "fungible": True,
            "sku": self.sku,
            "qty": self.qty,
            "userId": self.userId,
            "created": self.created.isoformat(),
            "expiration": self.expiration.isoformat(),
            "expired": self.expired,
        }
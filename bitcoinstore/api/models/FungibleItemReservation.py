import uuid
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime, timezone
from bitcoinstore.extensions import db


class FungibleItemReservation(db.Model):


    __tablename__ = 'fungible_item_reservation'


    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    sku = db.Column(db.String(100), db.ForeignKey('fungible_item.sku'))
    timestamp = db.Column(db.DateTime, nullable=False, default=db.func.now())
    quantity = db.Column(db.Integer, nullable=False, default=0)
    session = db.Column(db.String)


    def __repr__(self) -> str:
        return '<FungibleItemReservation ID %r>' % self.id


    def __init__(self, sku, quantity) -> None:
        if not sku.strip():
            raise Exception("FungibleItemReservation: SKU required")
        else:
            self.set_sku(sku)

        if not quantity or quantity == 0:
            raise Exception("FungibleItemReservation: SKU required")

        if quantity < 0:
            raise Exception("FungibleItemReservation: Quantity must be greater than 0")
        else:
            self.set_quantity(quantity)


    def get_quantity(self) -> int:
        return self.quantity


    def set_quantity(self, quantity: int) -> None:
        self.quantity = quantity


    def get_sku(self) -> str:
        return self.sku


    def set_sku(self, sku: str) -> None:
        self.sku = sku.strip()


    def get_timestamp(self) -> datetime:
        return self.timestamp


    def set_session(self, session: str) -> None:
        self.session = session

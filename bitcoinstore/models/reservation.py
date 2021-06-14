from bitcoinstore.extensions import db
from .product_item import ProductItem


class Reservation(db.Model):
    """Records a reservation for a specific product item"""

    id = db.Column(db.BigInteger, primary_key=True)
    product_item_id = db.Column(
        db.BigInteger, db.ForeignKey(ProductItem.id), nullable=False
    )
    product_item = db.relationship(
        "ProductItem",
        back_populates="reservations"
    )

    cart_id = db.Column(db.String, nullable=False)
    amount = db.Column(db.Integer, nullable=False)

    created_at = db.Column(
        db.DateTime, nullable=False, server_default=db.func.current_timestamp()
    )

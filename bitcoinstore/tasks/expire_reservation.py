from flask import current_app
from sqlalchemy.exc import DatabaseError

from bitcoinstore.extensions import db
from bitcoinstore.model.reservation import (
    FungibleReservation,
    NonFungibleReservation,
)


def expire(id, type):
    current_app.logger.info("expiring " + type.__name__ + " id=" + str(id))

    # TODO thread lock
    reservation = type.query.get(id)

    if not reservation:
        current_app.logger.error(
            "Error expiring reservation: NOT FOUND "
            + type.__name__
            + ".id="
            + str(id)
        )

    # if reservation is not expired do work, else do nothing
    if not reservation.expired:
        if isinstance(reservation, NonFungibleReservation):
            reservation.expired = True
            reservation.nonFungibleProduct.reserved = False
        elif isinstance(reservation, FungibleReservation):
            reservation.expired = True
            reservation.fungibleProduct.qty_reserved -= reservation.qty

        try:
            db.session.commit()
        except DatabaseError as e:
            current_app.logger.error(e)
            db.session.rollback()

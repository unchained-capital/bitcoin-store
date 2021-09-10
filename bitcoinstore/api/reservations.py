from http import HTTPStatus

from flask import Blueprint, jsonify, request, current_app
from sqlalchemy.exc import IntegrityError, DBAPIError

from bitcoinstore.extensions import db
from bitcoinstore.model.product import FungibleProduct, NonFungibleProduct
from bitcoinstore.model.reservation import (
    NonFungibleReservation,
    FungibleReservation,
)

reservations = Blueprint("reservations", __name__, template_folder="templates")

# TODO pagination
@reservations.get("fungible")
def queryFungible():
    query_params = []
    if request.args.get("sku"):
        query_params.append(FungibleReservation.sku == request.args.get("sku"))
    if request.args.get("userId"):
        query_params.append(
            FungibleReservation.userId == request.args.get("userId")
        )

    results = db.session.query(FungibleReservation).filter(*query_params).all()

    return jsonify(serialize(results)), HTTPStatus.OK


# TODO pagination
@reservations.get("nonfungible")
def queryNonFungible():
    query_params = []
    if request.args.get("userId"):
        query_params.append(
            NonFungibleReservation.userId == request.args.get("userId")
        )
    if request.args.get("serial"):
        query_params.append(
            NonFungibleReservation.serial == request.args.get("serial")
        )

    results = (
        db.session.query(NonFungibleReservation).filter(*query_params).all()
    )

    return jsonify(serialize(results)), HTTPStatus.OK


@reservations.get("fungible/<string:id>")
def getFungible(id):
    return getReservation(FungibleReservation, id)


@reservations.get("nonfungible/<string:id>")
def getNonFungible(id):
    return getReservation(NonFungibleReservation, id)


def getReservation(type, id):
    reservation = type.query.get(id)

    if not reservation:
        return "Not found: " + type.__name__ + ".id=" + id, HTTPStatus.NOT_FOUND
    return jsonify(serialize(reservation)), HTTPStatus.OK


@reservations.post("fungible")
def createFungible():
    if not request.json:
        return "payload required", HTTPStatus.BAD_REQUEST

    if request.json.get("sku") is None:
        return "sku is required", HTTPStatus.BAD_REQUEST

    if request.json.get("qty") is None:
        return "qty is required", HTTPStatus.BAD_REQUEST

    sku = request.json["sku"]
    req_qty = request.json["qty"]
    fp = (
        db.session.query(FungibleProduct)
        .filter(FungibleProduct.sku == sku)
        .first()
    )
    if not fp:
        return "FungibleProduct not found with sku=" + sku, HTTPStatus.NOT_FOUND

    if fp.qty - fp.qty_reserved < req_qty:
        return (
            "insufficient unreserved quantity. qty="
            + str(fp.qty)
            + " qty_reserved="
            + str(fp.qty_reserved),
            HTTPStatus.BAD_REQUEST,
        )
    else:
        # TODO figure out thread locks
        fp.qty_reserved += req_qty
        return create(FungibleReservation)


@reservations.post("nonfungible")
def createNonFungible():
    if not request.json:
        return "payload required", HTTPStatus.BAD_REQUEST

    if request.json.get("serial") is None:
        return "serial is required", HTTPStatus.BAD_REQUEST

    serial = request.json["serial"]
    nfp = (
        db.session.query(NonFungibleProduct)
        .filter(NonFungibleProduct.serial == serial)
        .first()
    )
    if not nfp:
        return (
            "NonFungibleProduct not found with serial=" + serial,
            HTTPStatus.NOT_FOUND,
        )

    if nfp.reserved:
        return "NonFungibleProduct is already reserved", HTTPStatus.BAD_REQUEST
    else:
        # TODO figure out thread locks
        nfp.reserved = True
        return create(NonFungibleReservation)


def create(type):
    if request.json.get("userId") is None:
        return "userId is required", HTTPStatus.BAD_REQUEST

    reservation = type()
    for key in type.__dict__.keys():
        # can't set id
        if key == "id":
            continue
        if key in request.json:
            setattr(reservation, key, request.json.get(key))

    db.session.add(reservation)
    error = commit()
    if error:
        return error

    return jsonify(reservation.serialize()), HTTPStatus.CREATED


@reservations.delete("fungible/<string:id>")
def expireFungible(id):
    return expireReservation(FungibleReservation, id)


@reservations.delete("nonfungible/<string:id>")
def expireNonFungible(id):
    return expireReservation(NonFungibleReservation, id)


def expireReservation(type, id):
    # TODO thread lock
    reservation = type.query.get(id)

    if not reservation:
        return "Not found: " + type.__name__ + ".id=" + id, HTTPStatus.NOT_FOUND

    # if reservation is not expired do work, else do nothing and return 204
    if not reservation.expired:
        if isinstance(reservation, NonFungibleReservation):
            reservation.expired = True
            reservation.nonFungibleProduct.reserved = False
        elif isinstance(reservation, FungibleReservation):
            reservation.expired = True
            reservation.fungibleProduct.qty_reserved -= reservation.qty

        error = commit()
        if error:
            return error

        return jsonify(reservation.serialize()), HTTPStatus.OK

    return "", HTTPStatus.NO_CONTENT


def serialize(reservations):
    if reservations is None:
        return []

    if isinstance(reservations, FungibleReservation):
        return FungibleReservation.serialize(reservations)
    elif isinstance(reservations, NonFungibleReservation):
        return NonFungibleReservation.serialize(reservations)

    serialized = []
    for reservation in reservations:
        if isinstance(reservation, FungibleReservation):
            serialized.append(FungibleReservation.serialize(reservation))
        elif isinstance(reservation, NonFungibleReservation):
            serialized.append(NonFungibleReservation.serialize(reservation))
        else:
            raise Exception(
                "list contains object that is not FungibleReservation or NonFungibleReservation"
            )

    return serialized


def commit():
    try:
        db.session.commit()
    except IntegrityError as ie:
        current_app.logger.info(ie)
        db.session.rollback()
        return ie.orig.diag.message_detail, HTTPStatus.CONFLICT
    except DBAPIError as dbe:
        current_app.logger.info(dbe)
        db.session.rollback()
        return str(dbe.orig), HTTPStatus.BAD_REQUEST

    # TODO match up other db errors with HTTP codes: HTTP 500 for non-user errors, etc.

    return None

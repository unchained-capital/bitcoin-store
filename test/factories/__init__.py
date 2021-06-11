from bitcoinstore.extensions import db
from bitcoinstore.models.product import Product

import factory
from faker import Factory as FakerFactory
from faker.providers import color, currency, isbn

from random import randint, random

faker = FakerFactory.create()
faker.add_provider(color)
faker.add_provider(currency)
faker.add_provider(isbn)


class ProductFactory(factory.alchemy.SQLAlchemyModelFactory):
    """Product factory."""

    sku = factory.Faker("isbn13")
    name = factory.Faker("name")
    description = factory.Faker("text")
    color = factory.Faker("color")
    unit_price_subunits = randint(1, 100000)
    unit_price_currency = factory.Faker("currency_code")
    shipping_weight_kg = random()

    class Meta:
        model = Product
        sqlalchemy_session = db.session
        sqlalchemy_session_persistence = "commit"

from bitcoinstore.extensions import db
from bitcoinstore.models.product import Product
from bitcoinstore.models.product_item import ProductItem

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

    class Meta:
        model = Product
        sqlalchemy_session = db.session
        sqlalchemy_session_persistence = "commit"


class ProductItemFactory(factory.alchemy.SQLAlchemyModelFactory):
    """Product Item factory."""

    # hack to generate product and id https://stackoverflow.com/a/51208287
    product = factory.SubFactory(ProductFactory)
    product_id = factory.LazyAttribute(lambda o: o.product.id)

    serial_num = factory.Faker("isbn13")
    description = factory.Faker("text")
    color = factory.Faker("color")
    unit_price_subunits = randint(1, 100000)
    unit_price_currency = factory.Faker("currency_code")
    shipping_weight_kg = random()
    amount_in_stock = randint(1, 100)

    class Meta:
        model = ProductItem
        sqlalchemy_session = db.session
        sqlalchemy_session_persistence = "commit"
        exclude = ["product"]

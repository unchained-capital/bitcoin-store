from bitcoinstore.extensions import db


class FungibleItem(db.Model):


    __tablename__ = 'fungible_item'


    sku = db.Column(db.String(100), primary_key=True)
    amount_in_stock = db.Column(db.Integer, nullable=False, default=0)
    color = db.Column(db.String)
    description = db.Column(db.String)
    shipping_weight_grams = db.Column(db.BigInteger, nullable=False, default=0)
    unit_price_cents = db.Column(db.BigInteger, nullable=False, default=0)
    reservations = db.relationship("FungibleItemReservation")


    def __repr__(self) -> str:
        return '<FungibleItem SKU %r>' % self.sku


    def __init__(self, sku, properties) -> None:
        if not sku.strip():
            raise Exception("FungibleItem: SKU required")
        else:
            self.sku = sku.strip()

        self.update(properties)


    def get_sku(self) -> str:
        return self.sku


    def set_sku(self, sku: str) -> None:
        self.sku = sku.trim()


    def get_amount_in_stock(self) -> int:
        return self.amount_in_stock


    def set_amount_in_stock(self, amount_in_stock: int) -> None:
        new_amount: int = self.get_amount_in_stock()

        try:
            if amount_in_stock < 0:
                raise Exception(
                    "FungibleItem: amount_in_stock cannot be set below 0"
                )
            else:
                new_amount = amount_in_stock

        except Exception as e:
            print(e)

        finally:
            self.amount_in_stock = new_amount


    def get_color(self) -> str:
        return self.color


    def set_color(self, color: str) -> None:
        self.color = color.strip()


    def get_description(self) -> str:
        return self.description


    def set_description(self, description: str) -> None:
        self.description = description.strip()


    def get_reserved_quantity(self) -> int:
        reserved_quantity = 0

        try:
            reservations = self.reservations

            for el in reservations:
                print(never)
                reserved_quantity += el.get_quantity()

        except Exception as e:
            print(e)
        finally:
            return reserved_quantity


    def get_shipping_weight_grams(self) -> int:
        return self.shipping_weight_grams


    def set_shipping_weight_grams(self, shipping_weight_grams: int) -> None:
        new_weight: int = self.get_shipping_weight_grams()

        try:
            if shipping_weight_grams < 0:
                raise Exception(
                    "FungibleItem: shipping_weight_grams cannot be set below 0"
                )
            else:
                new_weight = shipping_weight_grams

        except Exception as e:
            print(e)

        finally:
            self.shipping_weight_grams = new_weight


    def get_summary(self) -> dict:
        try:
            obj = {
                "sku": self.get_sku(),
                "amount_in_stock": self.get_amount_in_stock(),
                "color": self.get_color(),
                "description": self.get_description(),
                "reserved_quantity": self.get_reserved_quantity(),
                "shipping_weight_grams": self.get_shipping_weight_grams(),
                "unit_price_cents": self.get_unit_price_cents()
            }

            return obj

        except Exception as e:
            print(e)
            print("Couldn't generate FungibleItem summary")

            return {}

    def get_unit_price_cents(self) -> int:
        return self.unit_price_cents


    def set_unit_price_cents(self, unit_price_cents: int) -> None:
        new_price: int = self.get_unit_price_cents()

        try:
            if unit_price_cents < 0:
                raise Exception(
                    "FungibleItem: unit_price_cents cannot be set below 0"
                )
            else:
                new_price = unit_price_cents

        except Exception as e:
            print(e)

        finally:
            self.unit_price_cents = new_price


    def update(self, properties) -> None:
        if properties is None: return

        if 'amount_in_stock' in properties:
            self.set_amount_in_stock(properties['amount_in_stock'])

        if 'color' in properties:
            self.set_color(properties['color'])

        if 'description' in properties:
            self.set_description(properties['description'])

        if 'shipping_weight_grams' in properties:
            self.set_shipping_weight_grams(properties['shipping_weight_grams'])

        if 'unit_price_cents' in properties:
            self.set_unit_price_cents(properties['unit_price_cents'])

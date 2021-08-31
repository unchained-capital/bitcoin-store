from bitcoinstore.extensions import db


class NonFungibleItem(db.Model):


    __tablename__ = 'non_fungible_item'


    sn = db.Column(db.String(100), primary_key=True)
    color = db.Column(db.String)
    notes = db.Column(db.String)
    price_cents = db.Column(db.BigInteger, nullable=False, default=0)
    sold = db.Column(db.Boolean, nullable=False, default=False)
    sku = db.Column(db.String(100), db.ForeignKey('non_fungible_type.sku'))


    def __repr__(self) -> str:
        return '<NonFungibleItem SN %r>' % self.sn


    def __init__(self, sn, properties) -> None:
        if not sn.strip():
            raise Exception("NonFungibleItem: SN required")
        else:
            self.sn = sn.strip()

        self.update(properties)


    def get_sn(self) -> str:
        return self.sn


    def set_sn(self, sn: str) -> None:
        self.sn = sn.strip()


    def get_color(self) -> str:
        return self.color


    def set_color(self, color: str) -> None:
        self.color = color.strip()


    def get_notes(self) -> str:
        return self.notes


    def set_notes(self, notes: str) -> None:
        self.notes = notes.strip()


    def get_price_cents(self) -> int:
        return self.price_cents


    def set_price_cents(self, price_cents: int) -> None:
        new_price: int = self.get_price_cents()

        try:
            if price_cents < 0:
                raise Exception(
                    "NonFungibleItem: price_cents cannot be set below 0"
                )
            else:
                new_price = price_cents

        except Exception as e:
            print(e)

        finally:
            self.price_cents = new_price


    def get_sku(self) -> str:
        return self.sku


    def set_sku(self, sku: str) -> None:
        self.sku = sku.strip()


    def get_sold(self) -> bool:
        return self.sold


    def set_sold(self, sold: bool) -> None:
        self.sold = sold


    def get_summary(self) -> dict:
        try:
            obj = {
                "sn": self.get_sn(),
                "color": self.get_color(),
                "notes": self.get_notes(),
                "price_cents": self.get_price_cents(),
                "sku": self.get_sku(),
                "sold": self.get_sold()
            }

            return obj

        except Exception as e:
            print(e)
            print("Couldn't generate NonFungibleItem summary")

            return {}


    def update(self, properties) -> None:
        if properties is None: return

        if 'color' in properties:
            self.set_color(properties['color'])

        if 'notes' in properties:
            self.set_notes(properties['notes'])

        if 'price_cents' in properties:
            self.set_price_cents(properties['price_cents'])

        if 'sku' in properties:
            self.set_sku(properties['sku'])

        if 'sold' in properties:
            self.set_sold(properties['sold'])

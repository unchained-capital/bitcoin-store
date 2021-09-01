from bitcoinstore.extensions import db


class NonFungibleType(db.Model):


    __tablename__ = 'non_fungible_type'


    sku = db.Column(db.String(100), primary_key=True)
    description = db.Column(db.String)
    shipping_weight_grams = db.Column(db.BigInteger, nullable=False, default=0)
    items = db.relationship("NonFungibleItem")


    def __repr__(self) -> str:
        return '<NonFungibleType SKU %r>' % self.sku


    def __init__(self, sku, properties) -> None:
        if not sku.strip():
            raise Exception("NonFungibleType: SKU required")
        else:
            self.sku = sku.strip()

        self.update(properties)


    def get_sku(self) -> str:
        return self.sku


    def set_sku(self, sku: str) -> None:
        self.sku = sku.strip()


    def get_description(self) -> str:
        return self.description


    def set_description(self, description: str) -> None:
        self.description = description.strip()


    def get_shipping_weight_grams(self) -> int:
        return self.shipping_weight_grams


    def set_shipping_weight_grams(self, shipping_weight_grams: int) -> None:
        new_weight: int = self.get_shipping_weight_grams()

        try:
            if shipping_weight_grams < 0:
                raise Exception(
                    "NonFungibleType: shipping_weight_grams cannot be set below 0"
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
                "description": self.get_description(),
                "shipping_weight_grams": self.get_shipping_weight_grams()
            }

            return obj

        except Exception as e:
            print(e)
            print("Couldn't generate NonFungibleType summary")

            return {}


    def update(self, properties) -> None:
        if properties is None: return

        if 'description' in properties:
            self.set_description(properties['description'])

        if 'shipping_weight_grams' in properties:
            self.set_shipping_weight_grams(properties['shipping_weight_grams'])

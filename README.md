# A Backend for a Bitcoin store

This project aims to eventually become a bitcoin based store api,
including sections for inventory managment, product searches,
accepting bitcoin payments, and fulfillment.

Currently, very little of this functionality is present.

## Inventory Management

Somewhere, our store has a warehouse that holds products that we
want to sell. We need to track these products in order to sell them.

Generally, there are two large categories of products - fungible
and non-fungible. Fungible products are ones where the individual
product items are essentially interchangeable. These products are
identified by a SKU, they have a short name, a long description,
a per-unit-price (usually in USD), and a shipping weight. However,
the quantity on hand can just be represented by a number. An example
of a fungible item:

  Wooden Pencil, Yellow, #2, Pre-Sharpened, 30-pack
  SKU 12341234
  Unit Price: $3.00
  Shipping Weight: 0.1 kg
  Color: Yellow
  Amount in Stock: 973

Non-fungible inventory has more or less the same data descibing a
product, but each item of inventory is unique, and as such it has
a serial number that is unique to its product line. Also, non-fungible
items may have individual descriptions. An example of a non-fungible
item:

  Motorcyle, Honda CB750F
  SKU 91919191
  Shipping Weight: 200 kg

  Stock Item:
  SKU 91919191
  Color: Yellow
  SN: VIN1234134134
  Notes: Stratches on the clearcoat on the fuel tank.
  Price: $3200


The inventory api should include methods to add new products,
edit existing products. For fungible products, there should be
a way to update the current supply. For non-fungible products
there should be a way to add and edit particular product items.

Also, in anticipation of interfacing with a shopping cart, there
should be some api calls that can be used to reserve some products
while the user shops. These reservations can be ended in at least
three different ways - the first way happens when a purchase is
finalized, and the items are then removed from the inventory and
transferred to the (as yet unwritten) fullfillment service. The
second way is that the user can explicity remove an item from his
cart, in which case the cart will arrange to call the inventory
api removing the reservation. In the third case, reservations are
only valid for a certain amount of time (perhaps an hour). After
that time, a backend cleanup job will come through and automatically
remove the reservation.

### Adding a new fungible item without a SKU

Used for adding fungible items without a SKU. This creates an item SKU.

```
POST /api/fungible
<body application/json> {
    amount_in_stock: int | undefined
    color: str | undefined
    description: str | undefined
    shipping_weight_grams: int | undefined
    unit_price_cents: int | undefined
}
```

### Adding or updating a fungible item with a SKU

Used for adding or updating fungible items by their SKU. If the SKU exists, the item is updated else it is added.

```
PUT /api/fungible/<sku>
<body application/json> {
    amount_in_stock: int | undefined
    color: str | undefined
    description: str | undefined
    shipping_weight_grams: int | undefined
    unit_price_cents: int | undefined
}
```

### Retrieving a fungible item by SKU

```
GET /api/fungible/<sku>
```

### Fungible add quantity

Used for adding quantity to an item stock by SKU.

```
POST /api/fungible/<sku>/add/<quantity>
```

### Fungible remove quantity

Used for removing quantity from an item stock by SKU.

```
POST /api/fungible/<sku>/remove/<quantity>
```

### Adding or updating a non-fungible item with a serial number and SKU

Used for adding or updating non-fungible items by their serial number and SKU. If the serial number and SKU exist, the item or SKU type are updated else it is added.

```
PUT /api/non-fungible/<sku>/<sn>
<body application/json> {
    color: str | undefined
    description: str | undefined # This is a SKU parent type attribute
    notes: str | undefined
    price_cents: int | undefined
    shipping_weight_grams: int | undefined # This is a SKU parent type attribute
    sold: bool | undefined
}
```

### Retrieving a non-fungible item by SKU and serial number

```
GET /api/non-fungible/<sku>/<sn>
```

## Product Searches

TBD

## Bitcoin Payments

TBD

## Fulfillment

TBD

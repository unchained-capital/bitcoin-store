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

## Product Searches

TBD

## Bitcoin Payments

TBD

## Fulfillment

TBD
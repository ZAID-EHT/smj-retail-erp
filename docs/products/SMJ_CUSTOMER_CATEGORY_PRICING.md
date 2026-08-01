# SMJ Customer-Category Auto-Pricing on Sales

A sale auto-applies the **customer's Price Category** price. `get_cart_pricing` /
`get_bootstrap` price against `_customer_price_list(customer)` (the customer's
`default_price_list`, set as Price Category by the Customer quick form) via ERPNext's
own `get_item_details` — no pricing duplicated in Vue.

## Verified (test_customer_category_pricing, 3)
Product priced Wholesale 1200 / Retail 1500:
- Wholesale-category customer → **1200**
- Retail-category customer → **1500**
- Changing the customer reprices the cart.

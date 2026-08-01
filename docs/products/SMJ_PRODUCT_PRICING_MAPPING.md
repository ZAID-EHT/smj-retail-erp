# SMJ Product Pricing Mapping (two selling prices)

| Form field | Item Price list | Flag |
|-----------|-----------------|------|
| Cost Price | Buying Settings buying_price_list (Standard Buying) | buying |
| Wholesale Price | Wholesale Price List | selling |
| Retail Price | Retail Price List | selling |

Exactly **two selling prices** (Wholesale, Retail) plus Cost. Each is upserted as a
standard Item Price at the item's stock UOM, party-less, no duplicate rows; a cleared
price deletes its row. Writing requires Sales/Purchase Master Manager permission on
Item Price; the whole save is atomic. Margin (custom_margin) is a reference input.

## Auto-pricing on sales
A sale prices against the **customer's Price Category** (their default_price_list) via
get_cart_pricing → get_item_details. See docs/products/SMJ_CUSTOMER_CATEGORY_PRICING.md.

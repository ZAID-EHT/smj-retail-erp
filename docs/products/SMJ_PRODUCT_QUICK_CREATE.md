# SMJ Product Quick-Create

Routes: `/retail-erp/inventory/products/new` and `/inventory/products/:name/edit`.
Backend: `my_store_ui/quick_entry/product.py` (atomic `create_product`). Tests:
`test_product_quick_entry` (13), `test_quick_entry_security` (7), `test_batch_fifo` (1).

Sections/order: Basic Information (Product ID, SKU, Product Name, two drag-and-drop
images), Product Classification (Size, Category, Material, Carton Qty), Stock Setup
(3 Stock Locations, Re-Stock Qty, batch status), Pricing (Cost, Margin, Wholesale,
Retail).

- **Product ID** `P100001…` and **SKU** `5001…` auto-generated server-side
  (concurrency-safe make_autoname), read-only, immutable on edit.
- **Two selling prices only — Wholesale and Retail** — synced to standard Item Price
  (plus Cost→Standard Buying); no duplicates; permission-gated; atomic (savepoint).
- **Photos: drag-and-drop** (ImageUpload) via Frappe's `/api/method/upload_file`
  (PNG/JPG/WEBP/GIF ≤5 MB), thumbnail + Replace/Remove; URL stored in
  Item.image / custom_image_2.
- New stock products are **batch-managed**; stock quantity is never a Product field.
- Cost Price hidden from users without a master-manager role.

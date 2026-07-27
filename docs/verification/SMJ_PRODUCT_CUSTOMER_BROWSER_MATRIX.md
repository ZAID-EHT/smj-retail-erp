# SMJ Product/Customer Forms — Browser Matrix

Run 2026-07-27 on staging.local. Linux-native Playwright Chromium; closed via the
Playwright API. **108/108 checks, 0 problems**, 18 pages × 6 viewports.

| Viewport | Result |
|----------|--------|
| 1920×1080 | 18/18 |
| 1440×900 | 18/18 |
| 1024×768 | 18/18 |
| 768×1024 | 18/18 |
| 390×844 | 18/18 |
| 360×800 | 18/18 |

Includes the **Product quick-create** (18 fields, Product ID/SKU auto read-only, two
images, 3 warehouse selectors, pricing) and **Customer quick-create** (14 fields,
Business Nature once, Payment Type toggling credit fields) plus the updated Product
(SKU) and Customer (Business Nature) lists. Per page/viewport: HTTP status,
dead-route, horizontal overflow, console/page errors, DOM secret-leak heuristic — all
clean. No clipping, no overflow, mobile layouts pass.

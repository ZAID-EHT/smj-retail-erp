# SMJ Customer Quick-Create

Routes: `/retail-erp/sales/customers/new` and `/sales/customers/:name/edit`. Backend:
`my_store_ui/quick_entry/customer.py` (atomic `create_customer`). Tests:
`test_customer_quick_entry` (15), `test_quick_entry_security`, `test_customer_category_pricing`.

Sections: Customer Information (Customer, BR No, Business Nature [once], Created Date),
Contact and Address (Address, City, Contact No, WhatsApp No [with "same as contact"],
Account Dept No), Delivery (Transport Method, Transport Detail), Pricing and Credit
(Price Category, Payment Type, Credit Limit, Credit Days).

- Address + Contact are standard linked records (Dynamic Link); no duplicates on edit.
- **Price Category** is a selling Price List (buying rejected; default Retail) and
  **drives the sale price automatically** in Smart Sales.
- Payment Type maps to the existing custom_credit_type; Credit requires a limit; the
  credit fields are hidden for Non-Credit. Created Date is read-only.

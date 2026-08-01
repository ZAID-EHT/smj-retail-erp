# SMJ Customer Credit Mapping

| Visible | Backend | Notes |
|---------|---------|-------|
| Payment Type = Credit | custom_credit_type = "Credit Customer" | reuses existing field (no second classification) |
| Payment Type = Non-Credit | custom_credit_type = "Non-Credit Customer" | credit limit/days forced to 0 |
| Credit Limit | credit_limits child (per company) | standard ERPNext; read by get_credit_limit |
| Credit Days | custom_credit_days | used for due-date/overdue display |

- Credit requires a limit > 0. Non-Credit defaults limit/days to 0.
- **Safe conversion:** Credit → Non-Credit is refused when the customer has an
  outstanding balance. Historic balances are never erased.
- Existing credit enforcement (wholesale/credit.py delivery gate) is unchanged.

# SMJ Retail ERP — Visual Regression / Screenshot Evidence

**No screenshots were captured in this pass.** Playwright is not installed
in this environment:

```
$ python3 -c "import playwright"
ModuleNotFoundError: No module named 'playwright'
$ npx playwright --version
npm error UNABLE_TO_VERIFY_LEAF_SIGNATURE
```

Installing it would mean a network package install in an environment where
that already failed on a certificate error, and the mission's own
instructions say not to install system packages without approval. So this
step was skipped rather than faked.

What *was* verified, every time a batch of CSS/component changes landed:

```
cd apps/my_store_ui/frontend && npm run build
```

— which succeeded on every run (111 → 171 modules once icons were wired
in), meaning there are no Vue compilation errors, no broken imports, and no
syntax errors across the ~55 new icon components and every touched
stylesheet.

`bench serve` was confirmed running and reachable (`curl` → `200`) but no
authenticated page render was captured.

## For a follow-up session

1. Install Playwright (with approval) or use whatever browser automation is
   already configured for this project.
2. Log in, then screenshot Home, Smart Sales, Sales Orders, Products,
   Customers, Purchases, Finance, Transaction Register, Reports, a
   universal DocType list/detail/form, and Bank/Payment Reconciliation at
   1440×900, 768×1024 and 390×844.
3. Compare against `SMJ_Retail_ERP_UI_Design_Pack/01_generated_previews/*`
   and adjust spacing/density where they diverge — the token values will
   already match, so any remaining differences will be layout composition,
   not colour or typography.

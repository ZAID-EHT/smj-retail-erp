# SMJ Retail ERP — Component Library

## Icon pack

`frontend/src/components/icons/` — `IconBase.vue` is the shared wrapper
(24×24 viewBox, 1.8px rounded stroke, `currentColor`, accessible `<title>`
when not decorative, `aria-hidden` when decorative). All 25 icons required
by `ICON_PACK_SPEC.md` were built on top of it, plus ~29 utility icons
(search, notification, message, help, settings, profile, logout, new,
import, export, print, refresh, filter, columns, sort, calendar,
attachment, comments, share, assignment, submit, cancel, amend, hold,
resume, close, reopen, chevron, menu). `index.js` barrel-exports all of
them. `moduleIconMap.js` maps the existing route `meta.icon` strings onto
the module icons so no route metadata needed to change.

Every icon is a plain Vue SFC (e.g. `SmjHomeBuilding.vue`) with `size`,
`title` and `decorative` props — usage:

```vue
<SmjInvoiceDocumentSeal size="18" decorative />
<SmjSubmit size="16" title="Submit document" />
```

## Shared component pattern

This codebase's existing shared-component layer is CSS-class-based rather
than one Vue component per concept: `.ref-status-badge` / `.rug-status` /
`.rug-value-badge` (status pills), `.priority-metric` (KPI cards),
`.ref-data-table` / `.rug-table-region` / `.ru-table-wrap` (data tables with
built-in mobile card fallback), `.ref-detail-summary-card` (summary cards),
`.ref-button` (buttons). These classes are already reused across dozens of
templates and are now all token-driven (see
`SMJ_UI_DESIGN_SYSTEM.md`), which is what makes them "one design system"
in practice.

**Decision**: no new single-purpose Vue wrapper components (`KpiCard.vue`,
`StatusPill.vue`, etc.) were added on top of this. Adding them without also
migrating every template that already renders these patterns via CSS
classes would create two parallel, half-adopted systems — exactly the kind
of premature abstraction / dead code this project's own engineering
conventions warn against. The existing `src/components/ui/ColourCard.vue`,
`src/components/data/*`, `src/components/detail/*` and
`src/components/feedback/*` directories remain the actual shared component
set; they were audited and none needed structural changes, only the token
values flowing into their CSS.

## New shared infrastructure added this pass

- `frontend/src/composables/pageActions.js` — header page-action registry
  (see `SMJ_HEADER_NAVIGATION.md` for adoption status).
- `frontend/src/components/shell/HeaderPageActions.vue` — renders it.

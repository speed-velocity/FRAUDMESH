# FraudMesh UI QA surgery report

Branch: `ui/lamborghini`  
Audit command: `pnpm run ui:audit`  
Screenshots: [`before/`](before/) and [`after/`](after/)

## Phase 1–3 baseline

The harness covers Dashboard, Live Alerts, Investigation Cases, Fraud Network, Causal Chain, Evidence Explorer, Audit & Access, and login at 375, 768, 1280, and 1920px widths. It also records overflow, clipped text, touch-target sizing, font metrics, axe violations, console errors, HTTP failures, and screenshots.

Baseline recorded 258 findings. The findings are grouped below by shared root cause; each row represents every repeated occurrence of that issue across pages/viewports.

| ID | Pages / viewports | Selector pattern | Severity | Screenshot | Proposed fix |
|---|---|---|---|---|---|
| UI-001 | All authenticated pages, all widths | `.brand-mark.brand-logo`, `.brand-page-title` | major | [dashboard 375](before/dashboard-375.png) | Give the logo box a fixed flex size, prevent shrinking, and allow page titles to wrap safely. |
| UI-002 | All authenticated pages, all widths | `nav`, `a`, `.brand-page-title` | major | [cases 768](before/investigation-cases-768.png) | Add `min-width: 0`, `overflow-wrap: anywhere`, and consistent nav/control widths. |
| UI-003 | All pages, especially mobile | `.eyebrow`, `small`, `.count-badge`, `.secondary-action` | minor | [alerts 375](before/live-alerts-375.png) | Raise readable microcopy to the token minimum and reserve uppercase tracking for labels. |
| UI-004 | All pages, all widths | headings and brand text | major | [login 375](before/login-375.png) | Use relaxed line-height and `clamp()` headings without clipping. |
| UI-005 | All pages | muted labels and explanatory text | major | [dashboard 375](before/dashboard-375.png) | Raise muted text contrast to the AA-safe steel/smoke token. |
| UI-006 | Mobile pages | nav links, sign-out, menu, selects, inputs, review tabs | major | [audit 375](before/audit-access-375.png) | Standardize controls to a 48px mobile target and 44px minimum elsewhere. |
| UI-007 | Cases, Evidence, Audit | nested main landmarks / heading order | minor | [cases 375](before/investigation-cases-375.png) | Preserve existing routes while giving page sections explicit structural labels in the shared layout. |
| UI-008 | Header | `.app-brand` accessible-name mismatch | major | [alerts 375](before/live-alerts-375.png) | Keep the visible brand text inside the labelled link and make the logo image decorative. |

The complete raw baseline is in [`before-issues.json`](before-issues.json), including selector, page, viewport, severity, details, and screenshot path for every occurrence.

## Fix order

1. Shared tokens and typography: readable sizes, line-height, contrast, wrapping.
2. Header/sidebar/mobile navigation: fixed logo sizing, touch targets, focus states, drawer behavior.
3. Shared buttons, tabs, inputs, badges, cards, and table/graph panels.
4. Page-specific grid and long-ID fixes.
5. Re-run the same audit and compare `before/` with `after/`.

## Before/after checklist

| Page | Before screenshots | After screenshots | Result |
|---|---|---|---|
| Dashboard | captured | pending | pending fix pass |
| Live Alerts | captured | pending | pending fix pass |
| Investigation Cases | captured | pending | pending fix pass |
| Fraud Network | captured | pending | pending fix pass |
| Causal Chain | captured | pending | pending fix pass |
| Evidence Explorer | captured | pending | pending fix pass |
| Audit & Access | captured | pending | pending fix pass |
| Login | captured at 375px | pending | pending fix pass |

## Design decisions

- The Lamborghini black/charcoal/gold system remains intact; readability wins over tiny uppercase microcopy.
- No content, routes, API contracts, authentication behavior, or backend files are changed.
- The exact proprietary LamboType font is unavailable; the existing documented Roboto/Helvetica/Arial fallback remains.

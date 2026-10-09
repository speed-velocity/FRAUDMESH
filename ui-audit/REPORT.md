# FraudMesh UI QA surgery report

## Editorial redesign verification

Branch: `ui/editorial`  
Theme: `editorial` (default via `data-theme="editorial"`)  
Audit command: `$env:AUDIT_OUTPUT_DIR='editorial'; pnpm run ui:audit`

The editorial audit passed: 0 blocker, 0 major, 0 minor, 0 horizontal-overflow, and 0 axe findings. It generated 57 screenshots under [`ui-audit/editorial/`](editorial/), covering every authenticated route and login at 375, 768, 1280, and 1920px, plus mobile navigation, focus, Nemotron-unavailable, and long-ID states. Raw results are in [`editorial-issues.json`](editorial-issues.json).

The redesign uses one semantic token file with a `data-theme` switch. Editorial is the default; neoclassical values are also shipped for a future switch. Playfair Display, Source Serif 4, and IBM Plex Mono are loaded from Google Fonts; no proprietary font substitution was needed. Existing route structure, API calls, authentication, labels, graph interactions, and review flows remain unchanged.

Accessibility/layout fixes included one authenticated `<main>` landmark, named content regions, corrected heading levels, 48px controls, 48px mobile touch targets, long-ID wrapping, graph width constraints, and exact/inferred/weak graph edge styles that remain distinguishable without colour alone.

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
| Dashboard | captured | [375](after/dashboard-375.png), [768](after/dashboard-768.png), [1280](after/dashboard-1280.png), [1920](after/dashboard-1920.png) | pass |
| Live Alerts | captured | [375](after/live-alerts-375.png), [768](after/live-alerts-768.png), [1280](after/live-alerts-1280.png), [1920](after/live-alerts-1920.png) | pass |
| Investigation Cases | captured | [375](after/investigation-cases-375.png), [768](after/investigation-cases-768.png), [1280](after/investigation-cases-1280.png), [1920](after/investigation-cases-1920.png) | pass |
| Fraud Network | captured | [375](after/fraud-network-375.png), [768](after/fraud-network-768.png), [1280](after/fraud-network-1280.png), [1920](after/fraud-network-1920.png) | pass |
| Causal Chain | captured | [375](after/causal-chain-375.png), [768](after/causal-chain-768.png), [1280](after/causal-chain-1280.png), [1920](after/causal-chain-1920.png) | pass |
| Evidence Explorer | captured | [375](after/evidence-explorer-375.png), [768](after/evidence-explorer-768.png), [1280](after/evidence-explorer-1280.png), [1920](after/evidence-explorer-1920.png) | pass |
| Audit & Access | captured | [375](after/audit-access-375.png), [768](after/audit-access-768.png), [1280](after/audit-access-1280.png), [1920](after/audit-access-1920.png) | pass |
| Login | captured at 375px | [375](after/login-375.png) | pass |

Final audit result: 76 minor findings, 0 major findings, 0 blockers, 0 axe serious/critical findings, and 0 document/element horizontal-overflow findings. Raw final results are in [`after-issues.json`](after-issues.json).

The final run also exercised the mocked/synthetic alert, selected alert detail, mobile sidebar-expanded state, focus state, Nemotron-unavailable state, case, graph, evidence, audit-empty state, and login states. These additional state screenshots are in [`after/`](after/). The audit command remains deterministic and billable-API free.

## Remaining known issues

The remaining minor axe findings are structural: the shared authenticated shell uses a `<main>` landmark around pages whose page-specific experience roots are also `<main>`, and some page headings begin at `h3` because the existing component text hierarchy is preserved. They do not create serious/critical axe violations or visual overflow. Resolving them cleanly would require semantic JSX changes beyond this CSS-focused surgery pass.

## Design decisions

- The Lamborghini black/charcoal/gold system remains intact; readability wins over tiny uppercase microcopy.
- No content, routes, API contracts, authentication behavior, or backend files are changed.
- The exact proprietary LamboType font is unavailable; the existing documented Roboto/Helvetica/Arial fallback remains.

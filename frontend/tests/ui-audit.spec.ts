import { test, expect, type Page, type Response } from "@playwright/test";
import axe from "axe-core";
import fs from "node:fs/promises";
import path from "node:path";

type Viewport = { name: string; width: number; height: number };
type AuditIssue = { id: string; page: string; viewport: string; selector: string; severity: string; details: string; screenshot: string };

const ROOT = path.resolve(process.cwd(), "..");
const PHASE = process.env.AUDIT_PHASE === "after" ? "after" : "before";
const viewports: Viewport[] = [
  { name: "375", width: 375, height: 812 }, { name: "768", width: 768, height: 1024 },
  { name: "1280", width: 1280, height: 800 }, { name: "1920", width: 1920, height: 1080 },
];
const pages = [
  ["dashboard", "#dashboard"], ["live-alerts", "#alerts"], ["investigation-cases", "#cases"],
  ["fraud-network", "#network"], ["causal-chain", "#chain"], ["evidence-explorer", "#evidence"], ["audit-access", "#audit"],
] as const;
const synthetic = {
  summary: { counts: { active_investigations: 3, priority_alerts: 2, connected_entities: 12, evidence_records: 24 }, alerts: [{ entity_id: "ACC-VERY-LONG-IDENTIFIER-001", score: 0.94, band: "critical", amount_inr: 394000, reasons: ["9 victim payments from 9 senders", "aggregate victim payment value exceeds INR 100,000", "a complaint references an entity already present in the network", "inbound value was forwarded within one hour"], evidence_ids: ["E-0093", "E-0094", "E-0095"], status: "escalate" }] },
  network: { nodes: [{ entity_id: "ACC-VERY-LONG-IDENTIFIER-001", type: "BankAccount" }, { entity_id: "ENT-08", type: "Person/Entity" }, { entity_id: "DEV-001", type: "Device" }, { entity_id: "CASE-001", type: "Case" }], edges: [{ source: "ACC-VERY-LONG-IDENTIFIER-001", target: "ENT-08", count: 9, kind: "exact", evidence_ids: "E-0093,E-0094" }, { source: "ENT-08", target: "DEV-001", count: 2, kind: "inferred", evidence_ids: "E-0100" }, { source: "DEV-001", target: "CASE-001", count: 1, kind: "weak", evidence_ids: "E-0101" }] },
  evidence: { records: [{ evidence_id: "E-0093", type: "transaction", source_file: "ledger_transactions.csv", source_row: 93, ts_utc: "2026-10-09T20:17:46Z", raw_text: "INR 394000 linked transfer from ACC-VERY-LONG-IDENTIFIER-001" }, { evidence_id: "E-0100", type: "complaint", source_file: "complaints.csv", source_row: 100, ts_utc: "2026-10-09T20:18:11Z", raw_text: "Complaint references ENT-08 and a linked account." }] },
  cases: { cases: [{ case_id: "CASE-001", entity_id: "ACC-VERY-LONG-IDENTIFIER-001", score: 0.94, title: "Critical linked payment review", notes: "Review linked transaction evidence.", status: "open" }] },
  evaluation: { available: false }, controls: { controls: [{ name: "synthetic_data", status: "enabled", detail: "Synthetic records loaded." }] }, events: { events: [{ event_id: "EV-0001", kind: "transfer", status: "accepted", ts: "2026-10-09T20:17:46Z" }] },
};

async function json(response: Response, body: unknown, status = 200) { await response.fulfill({ status, contentType: "application/json", body: JSON.stringify(body) }); }

async function mockApi(page: Page, authenticated = true) {
  await page.route("http://127.0.0.1:8000/**", async (route) => {
    const url = new URL(route.request().url());
    if (url.pathname.endsWith("/auth/me")) return json(route, { username: "investigator", role: "investigator" });
    if (url.pathname.endsWith("/auth/login")) return json(route, { access_token: "ui-audit-token" });
    if (url.pathname.endsWith("/dashboard/summary")) return json(route, authenticated ? synthetic.summary : { detail: "Not authenticated" }, authenticated ? 200 : 401);
    if (url.pathname.endsWith("/network")) return json(route, synthetic.network);
    if (url.pathname.includes("/cases/") && url.pathname.endsWith("/evidence")) return json(route, { records: [{ evidence_id: "E-0093", txn_id: "TXN-0093", kind: "transfer", ts_utc: "2026-10-09T20:17:46Z", channel: "upi", amount_inr: 394000, from_entity: "ACC-VERY-LONG-IDENTIFIER-001", to_entity: "ENT-08", reference_text: "Linked transfer" }] });
    if (url.pathname.endsWith("/evidence")) return json(route, synthetic.evidence);
    if (url.pathname.endsWith("/cases")) return json(route, synthetic.cases);
    if (url.pathname.endsWith("/evaluation")) return json(route, synthetic.evaluation);
    if (url.pathname.endsWith("/meta/limitations")) return json(route, synthetic.controls);
    if (url.pathname.endsWith("/events")) return json(route, synthetic.events);
    if (url.pathname.endsWith("/simulator/status")) return json(route, { index: 0, total: 2, next_event: { event_id: "EV-NEXT-001", kind: "transfer", amount_inr: 394000, ts: "2026-10-09T20:17:46Z" } });
    if (url.pathname.includes("/alerts/") && url.pathname.endsWith("/actions")) return json(route, { actions: [] });
    if (url.pathname.includes("/contradictions")) return json(route, { conflicts: [] });
    if (url.pathname.includes("/findings")) return json(route, { findings: [] });
    if (url.pathname.includes("/hypotheses")) return json(route, { hypotheses: [] });
    if (url.pathname.includes("/plan")) return json(route, { steps: [] });
    if (url.pathname.includes("/reasoning")) return json(route, { label: "Nemotron unavailable", summary: "Live reasoning is unavailable in this audit harness." }, 503);
    if (url.pathname.includes("/audit")) return json(route, { records: [] });
    if (url.pathname.includes("/path")) return json(route, { found: false, hops: 0, nodes: [], edges: [] });
    return json(route, {});
  });
}

async function collectIssues(page: Page, pageName: string, viewport: Viewport, screenshot: string): Promise<AuditIssue[]> {
  const axeResults = await page.evaluate(async (source) => { (0, eval)(source); return await (window as any).axe.run(document); }, axe.source);
  const dom = await page.evaluate(() => {
    const visible = (element: Element) => { const rect = (element as HTMLElement).getBoundingClientRect(); return rect.width > 0 && rect.height > 0; };
    const overflowing: string[] = []; const small: string[] = []; const clipped: string[] = [];
    document.querySelectorAll("*").forEach((element) => {
      if (!(element instanceof HTMLElement) || !visible(element)) return;
      const selector = element.id ? `#${element.id}` : element.className && typeof element.className === "string" ? `.${element.className.split(/\s+/).filter(Boolean).slice(0, 2).join(".")}` : element.tagName.toLowerCase();
      if (element.scrollWidth > element.clientWidth + 1) overflowing.push(selector);
      const style = getComputedStyle(element); const fontSize = parseFloat(style.fontSize); const lineHeight = parseFloat(style.lineHeight);
      if (fontSize < 12) small.push(`${selector} (${fontSize}px)`);
      if (element.scrollWidth > element.clientWidth + 1 && style.overflowX === "hidden") clipped.push(selector);
      if (lineHeight && fontSize >= 14 && lineHeight / fontSize < 1.3) clipped.push(`${selector} line-height ${style.lineHeight}`);
    });
    const controls = [...document.querySelectorAll<HTMLElement>("button, a, input, select, textarea")].filter(visible).map((element) => { const rect = element.getBoundingClientRect(); return { selector: element.id ? `#${element.id}` : element.tagName.toLowerCase(), width: rect.width, height: rect.height, text: element.textContent?.trim() || (element as HTMLInputElement).placeholder || "" }; });
    const fonts = [...document.fonts].map((font) => ({ family: font.family, status: font.status }));
    return { overflowing: [...new Set(overflowing)], small: [...new Set(small)], clipped: [...new Set(clipped)], controls, fonts, width: innerWidth, scrollWidth: document.documentElement.scrollWidth };
  });
  const issues: AuditIssue[] = [];
  if (dom.scrollWidth > viewport.width + 1) issues.push({ id: "OVERFLOW-DOCUMENT", page: pageName, viewport: viewport.name, selector: "document", severity: "major", details: `document scrollWidth ${dom.scrollWidth} > ${viewport.width}`, screenshot });
  if (dom.overflowing.length) issues.push({ id: "OVERFLOW-ELEMENT", page: pageName, viewport: viewport.name, selector: dom.overflowing.slice(0, 4).join(", "), severity: "major", details: "Visible element has scrollWidth greater than clientWidth.", screenshot });
  if (dom.small.length) issues.push({ id: "TEXT-SIZE", page: pageName, viewport: viewport.name, selector: dom.small.slice(0, 4).join(", "), severity: "minor", details: "Visible text is below 12px.", screenshot });
  if (dom.clipped.length) issues.push({ id: "TEXT-CLIP", page: pageName, viewport: viewport.name, selector: dom.clipped.slice(0, 4).join(", "), severity: "major", details: "Content is clipped or line-height is too tight.", screenshot });
  for (const violation of axeResults.violations) issues.push({ id: `AXE-${violation.id}`, page: pageName, viewport: viewport.name, selector: violation.nodes.slice(0, 2).flatMap((node: any) => node.target).join(", "), severity: violation.impact === "critical" || violation.impact === "serious" ? "major" : "minor", details: violation.help, screenshot });
  for (const control of dom.controls.filter((item) => viewport.width < 768 && (item.width < 44 || item.height < 44))) issues.push({ id: "TOUCH-TARGET", page: pageName, viewport: viewport.name, selector: control.selector, severity: "major", details: `${control.text || "control"} is ${Math.round(control.width)}×${Math.round(control.height)}px.`, screenshot });
  return issues;
}

test("FraudMesh UI audit across routes and responsive viewports", async ({ browser }) => {
  const issues: AuditIssue[] = [];
  await fs.mkdir(path.join(ROOT, "ui-audit", PHASE), { recursive: true });
  for (const [pageName, hash] of pages) for (const viewport of viewports) {
    const context = await browser.newContext({ viewport: { width: viewport.width, height: viewport.height }, colorScheme: "dark" });
    const page = await context.newPage(); await mockApi(page); await page.addInitScript(() => localStorage.setItem("fraudmesh_token", "ui-audit-token"));
    const consoleErrors: string[] = []; const failed: string[] = [];
    page.on("console", (message) => { if (message.type() === "error") consoleErrors.push(message.text()); }); page.on("response", (response) => { if (response.status() >= 400 && !response.url().includes("favicon")) failed.push(`${response.status()} ${response.url()}`); });
    await page.goto(`${hash}`, { waitUntil: "domcontentloaded" }); await page.waitForTimeout(500);
    const screenshotPath = path.join(ROOT, "ui-audit", PHASE, `${pageName}-${viewport.name}.png`); await page.screenshot({ path: screenshotPath, fullPage: true });
    issues.push(...await collectIssues(page, pageName, viewport, `ui-audit/${PHASE}/${pageName}-${viewport.name}.png`));
    if (consoleErrors.length) issues.push({ id: "CONSOLE-ERROR", page: pageName, viewport: viewport.name, selector: "console", severity: "major", details: consoleErrors.slice(0, 2).join(" | "), screenshot: `ui-audit/${PHASE}/${pageName}-${viewport.name}.png` });
    if (failed.length) issues.push({ id: "HTTP-ERROR", page: pageName, viewport: viewport.name, selector: "network", severity: "major", details: failed.slice(0, 2).join(" | "), screenshot: `ui-audit/${PHASE}/${pageName}-${viewport.name}.png` });
    await context.close();
  }
  const loginContext = await browser.newContext({ viewport: { width: 375, height: 812 }, colorScheme: "dark" }); const login = await loginContext.newPage(); await mockApi(login, false); await login.goto("/?protected=1#dashboard", { waitUntil: "domcontentloaded" }); await login.waitForTimeout(500); await login.screenshot({ path: path.join(ROOT, "ui-audit", PHASE, "login-375.png"), fullPage: true }); issues.push(...await collectIssues(login, "login", viewports[0], `ui-audit/${PHASE}/login-375.png`)); await loginContext.close();
  await fs.writeFile(path.join(ROOT, "ui-audit", `${PHASE}-issues.json`), JSON.stringify(issues, null, 2));
  expect(issues.filter((issue) => issue.severity === "blocker")).toHaveLength(0);
});

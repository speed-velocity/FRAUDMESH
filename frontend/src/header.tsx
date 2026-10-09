import { useState, type ReactNode } from "react";

export type HeaderUser = { username: string; role: string };
export type HeaderPage = { title: string };

type Mode = "light" | "dark";

function currentMode(): Mode { return typeof document !== "undefined" && document.documentElement.dataset.mode === "dark" ? "dark" : "light"; }

function applyMode(mode: Mode): void {
  document.documentElement.dataset.mode = mode;
  try { window.localStorage.setItem("fraudmesh_mode", mode); } catch { /* storage may be blocked */ }
  const meta = document.querySelector<HTMLMetaElement>('meta[name="theme-color"]');
  const colour = getComputedStyle(document.documentElement).getPropertyValue("--fm-meta-theme").trim();
  if (meta && colour) meta.content = colour;
}

export function ModeToggle() {
  const [mode, setMode] = useState<Mode>(currentMode);
  const nextMode: Mode = mode === "dark" ? "light" : "dark";
  const label = nextMode === "dark" ? "Switch to dark mode" : "Switch to light mode";
  return <button className="mode-toggle" data-testid="mode-toggle" type="button" aria-label={label} aria-pressed={mode === "dark"} title={label} onClick={() => { applyMode(nextMode); setMode(nextMode); }}>
    <svg className="mode-toggle-icon" viewBox="0 0 24 24" aria-hidden="true" focusable="false">{mode === "dark" ? <><circle cx="12" cy="12" r="4" /><path d="M12 2v2M12 20v2M4.93 4.93l1.41 1.41M17.66 17.66l1.41 1.41M2 12h2M20 12h2M4.93 19.07l1.41-1.41M17.66 6.34l1.41-1.41" /></> : <path d="M20.5 15.2A8.5 8.5 0 0 1 8.8 3.5 8.5 8.5 0 1 0 20.5 15.2Z" />}</svg>
  </button>;
}

export function Header({ page, user, onSignOut }: { page: HeaderPage; user: HeaderUser; onSignOut: () => void }) {
  return <header className="app-header" data-testid="header">
    <a className="app-brand" data-testid="brand" href="#dashboard" aria-label={`FraudMesh ${page.title.toLowerCase()}`}>
      <span className="brand-mark brand-logo" aria-hidden="true"><img src="/assets/fraudmesh-logo-for-dark.png" alt="" /></span>
      <h1 className="brand-page-title" data-testid="page-title">{page.title}</h1>
    </a>
    <div className="header-wordmark" aria-label="FraudMesh intelligence platform">
      <strong className="wordmark-live"><span>FRAUD</span><span className="wordmark-accent">MESH</span></strong>
    </div>
    <div className="header-actions">
      <div className="role-chip" data-testid="role-chip">
        <span className="avatar">{user.role.slice(0, 1).toUpperCase()}</span>
      </div>
      <ModeToggle />
      <button className="sign-out" data-testid="sign-out" type="button" onClick={onSignOut}>Sign out</button>
    </div>
  </header>;
}

export function SafetyBanner(): ReactNode {
  return <div className="banner" data-testid="safety-banner">Synthetic data. Investigation-support prototype. Not for enforcement decisions.</div>;
}

export async function runSignOut(logout: () => Promise<unknown>, storage: Pick<Storage, "removeItem">): Promise<void> {
  try {
    await logout();
  } finally {
    storage.removeItem("fraudmesh_token");
  }
}

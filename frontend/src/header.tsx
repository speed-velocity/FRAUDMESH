import { type ReactNode } from "react";

export type HeaderUser = { username: string; role: string };
export type HeaderPage = { title: string };

export function Header({ page, user, onSignOut }: { page: HeaderPage; user: HeaderUser; onSignOut: () => void }) {
  return <header className="app-header" data-testid="header">
    <a className="app-brand" data-testid="brand" href="#dashboard" aria-label="FraudMesh dashboard">
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

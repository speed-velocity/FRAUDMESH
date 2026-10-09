import { describe, expect, it } from "vitest";
import { renderToStaticMarkup } from "react-dom/server";
import { createElement } from "react";
import { Header, runSignOut } from "./header";

describe("FraudMesh shell", () => {
  it("renders the shared brand, page title, role chip, and sign-out control", () => {
    const markup = renderToStaticMarkup(createElement(Header, { page: { title: "DASHBOARD" }, user: { username: "investigator", role: "investigator" }, onSignOut: () => undefined }));
    expect(markup).toContain("FRAUD");
    expect(markup).toContain("MESH");
    expect(markup).toContain("wordmark-accent");
    expect(markup).toContain("DASHBOARD");
    expect(markup).toContain('data-testid="role-chip"');
    expect(markup).toContain('data-testid="sign-out"');
  });

  it("renders the admin role variant without changing the shared navigation contract", () => {
    const markup = renderToStaticMarkup(createElement(Header, { page: { title: "AUDIT & ACCESS" }, user: { username: "admin", role: "admin" }, onSignOut: () => undefined }));
    expect(markup).toContain('class="avatar">A</span>');
    expect(markup).toContain('data-testid="header"');
  });

  it("runs logout and clears the session token", async () => {
    let called = false;
    let removed = "";
    await runSignOut(async () => { called = true; }, { removeItem: (key) => { removed = key; } });
    expect(called).toBe(true);
    expect(removed).toBe("fraudmesh_token");
  });
});


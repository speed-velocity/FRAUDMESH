import { readFileSync } from "node:fs";
import { describe, expect, it } from "vitest";

const asset = (name: string) => readFileSync(new URL(`../public/assets/nemo/${name}`, import.meta.url), "utf8");

describe("Nemo avatar asset integrity", () => {
  it("keeps the small icon head-only", () => {
    const icon = asset("nemo-icon.svg");
    expect(icon).toContain('id="eye-left"');
    expect(icon).not.toContain('id="arm-left"');
  });

  it("keeps the large avatar full-body", () => {
    const avatar = asset("nemo-avatar.svg");
    expect(avatar).toContain('id="arm-left"');
    expect(avatar).toContain('id="foot-left"');
  });
});

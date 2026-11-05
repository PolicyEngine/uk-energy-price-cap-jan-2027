import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import PreReleaseBanner from "./PreReleaseBanner";

const root = resolve(__dirname, "../..");

describe("pre-release safeguards", () => {
  it("renders the banner", () => {
    render(<PreReleaseBanner />);
    expect(screen.getByTestId("pre-release-banner").textContent).toMatch(
      /pre-release template — placeholder figures/i,
    );
  });

  it("layout renders the banner on every page and sets noindex", () => {
    const layout = readFileSync(resolve(root, "app/layout.jsx"), "utf8");
    expect(layout).toContain("<PreReleaseBanner />");
    expect(layout).toMatch(/robots:\s*\{\s*index:\s*false,\s*follow:\s*false/);
  });

  it("Next config sends X-Robots-Tag noindex", () => {
    const config = readFileSync(resolve(root, "next.config.mjs"), "utf8");
    expect(config).toContain('"X-Robots-Tag", value: "noindex, nofollow"');
  });
});

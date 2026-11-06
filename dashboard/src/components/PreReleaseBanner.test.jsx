import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import { render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";
import { bannerText, downloadName, isMock, pageTitle } from "../utils/releaseMode";
import PreReleaseBanner from "./PreReleaseBanner";

const root = resolve(__dirname, "../..");

afterEach(() => vi.unstubAllEnvs());

describe("pre-release safeguards", () => {
  it("renders the template banner by default", () => {
    render(<PreReleaseBanner />);
    expect(screen.getByTestId("pre-release-banner").textContent).toMatch(/pre-release template — placeholder figures/i);
  });

  it("a drill build (NEXT_PUBLIC_MOCK=1) says MOCK on the banner, title and downloads", () => {
    vi.stubEnv("NEXT_PUBLIC_MOCK", "1");
    expect(isMock()).toBe(true);
    expect(bannerText()).toMatch(/^MOCK/);
    expect(pageTitle("Energy price cap")).toBe("MOCK: Energy price cap");
    expect(downloadName("cap-history.csv")).toBe("MOCK-cap-history.csv");
    render(<PreReleaseBanner />);
    expect(screen.getByTestId("pre-release-banner").textContent).toMatch(/^MOCK/);
  });

  it("any other value is not a drill build", () => {
    vi.stubEnv("NEXT_PUBLIC_MOCK", "0");
    expect(isMock()).toBe(false);
    expect(downloadName("x.csv")).toBe("x.csv");
  });

  it("layout renders the banner on every page and sets noindex", () => {
    const layout = readFileSync(resolve(root, "app/layout.jsx"), "utf8");
    expect(layout).toContain("<PreReleaseBanner />");
    expect(layout).toMatch(/robots:\s*\{\s*index:\s*false,\s*follow:\s*false/);
  });

  it("Next config sends X-Robots-Tag noindex", () => {
    const config = readFileSync(resolve(root, "next.config.mjs"), "utf8");
    expect(config).toContain('{ key: "X-Robots-Tag", value: "noindex, nofollow" }');
    expect(config).toContain("basePath: false");
  });
});

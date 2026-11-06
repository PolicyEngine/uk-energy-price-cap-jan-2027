/** @type {import('next').NextConfig} */
// One source for the base path: the components read the same file for plain
// <img src> URLs. Planned address only: nothing deploys from this repository.
import { execSync } from "node:child_process";
import { readFileSync } from "node:fs";
import basePathConfig from "./src/lib/basePath.json" with { type: "json" };

const { basePath } = basePathConfig;

// The commit and engine versions the page was built from, baked in at build
// time for the Methodology tab's replication line and the policy links, as
// the Autumn Budget 2026 dashboard bakes its versions (next.config.ts).
function commitSha() {
  if (process.env.NEXT_PUBLIC_COMMIT_SHA) return process.env.NEXT_PUBLIC_COMMIT_SHA;
  try {
    return execSync("git rev-parse HEAD", { stdio: ["ignore", "pipe", "ignore"] }).toString().trim();
  } catch {
    return "";
  }
}

function lockedVersion(name) {
  try {
    const lock = readFileSync(new URL("../uv.lock", import.meta.url), "utf8");
    const match = lock.match(new RegExp(`\\[\\[package\\]\\]\\nname = "${name}"\\nversion = "([^"]+)"`));
    return match ? match[1] : "";
  } catch {
    return "";
  }
}

const nextConfig = {
  reactStrictMode: true,
  transpilePackages: ["@policyengine/ui-kit"],
  basePath,
  env: {
    NEXT_PUBLIC_COMMIT_SHA: commitSha(),
    NEXT_PUBLIC_POLICYENGINE_UK_VERSION: lockedVersion("policyengine-uk"),
  },
  // Pre-release template: keep every page out of search indexes, under the
  // base path and outside it (a stray address such as / too).
  async headers() {
    const noindex = [{ key: "X-Robots-Tag", value: "noindex, nofollow" }];
    return [
      { source: "/:path*", headers: noindex },
      { source: "/:path*", basePath: false, headers: noindex },
    ];
  },
};

export default nextConfig;

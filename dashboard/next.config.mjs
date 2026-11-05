/** @type {import('next').NextConfig} */
// One source for the base path: the components read the same file for plain
// <img src> URLs. Planned address only: nothing deploys from this repository.
import basePathConfig from "./src/lib/basePath.json" with { type: "json" };

const { basePath } = basePathConfig;

const nextConfig = {
  reactStrictMode: true,
  transpilePackages: ["@policyengine/ui-kit"],
  basePath,
  // Pre-release template: keep every page out of search indexes.
  async headers() {
    return [
      {
        source: "/:path*",
        headers: [{ key: "X-Robots-Tag", value: "noindex, nofollow" }],
      },
    ];
  },
};

export default nextConfig;

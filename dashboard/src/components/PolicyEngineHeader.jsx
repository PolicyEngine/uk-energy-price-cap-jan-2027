import { basePath as BASE_PATH } from "../lib/basePath.json";

// PolicyEngine site header, rendered by the dashboard itself. The planned
// address is policyengine.org/uk/energy-price-cap-jan-2027 (no route exists yet;
// nothing deploys from this repository). Static, not sticky, so the tool's own
// sticky title row keeps the top of the viewport.
const NAV_LINKS = [
  { label: "Research", href: "https://policyengine.org/uk/research" },
  { label: "Model", href: "https://policyengine.org/uk/model" },
  { label: "API", href: "https://policyengine.org/uk/api" },
  { label: "About", href: "https://policyengine.org/uk/about" },
  { label: "Donate", href: "https://policyengine.org/uk/donate" },
];

export default function PolicyEngineHeader() {
  return (
    <nav
      className="relative z-[1] w-full"
      style={{
        background:
          "linear-gradient(to right, var(--pe-color-primary-800, #234E52), var(--pe-color-primary-600, #2C7A7B))",
      }}
    >
      <div className="mx-auto flex h-[58px] max-w-[1400px] items-center gap-8 px-6 md:px-8">
        <a
          href="https://policyengine.org/uk"
          aria-label="PolicyEngine UK home"
          className="flex flex-shrink-0 items-center"
        >
          {/* eslint-disable-next-line @next/next/no-img-element */}
          <img
            src={`${BASE_PATH}/assets/logos/policyengine-white.svg`}
            alt="PolicyEngine"
            className="h-6 w-auto"
          />
        </a>

        <div className="hidden items-center gap-6 sm:flex md:gap-8">
          {NAV_LINKS.map((link) => (
            <a
              key={link.label}
              href={link.href}
              className="text-[15px] font-medium text-white no-underline transition-opacity hover:opacity-80"
            >
              {link.label}
            </a>
          ))}
        </div>
      </div>
    </nav>
  );
}

import { PolicyEngineShell } from "@policyengine/ui-kit/layout";
import "@policyengine/ui-kit/styles.css";
import localFont from "next/font/local";
import PolicyEngineFooter from "../src/components/PolicyEngineFooter";
import PreReleaseBanner from "../src/components/PreReleaseBanner";
import { pageTitle } from "../src/utils/releaseMode";
import { SITE_HEADER_STYLES, SITE_NAV_ITEMS } from "../src/utils/siteNav";

import "./globals.css";
import "./fonts.css";
import "./siteHeader.css";

// Inter, committed with the page (fonts/: the variable face, Latin subset;
// SIL Open Font License in fonts/OFL.txt), as on the Autumn Budget 2026
// dashboard: the build fetches nothing from Google.
const inter = localFont({
  src: "./fonts/inter-latin-variable.woff2",
  weight: "100 900",
  style: "normal",
  display: "swap",
  variable: "--font-inter",
  adjustFontFallback: "Arial",
});

export const metadata = {
  title: pageTitle("Energy price cap, January to March 2027 (pre-release template) | PolicyEngine"),
  description:
    "Pre-release template of the PolicyEngine dashboard for the January to March 2027 energy price cap. All figures are placeholders.",
  // Pre-release template: never indexed. Removed only in the G4 go-public
  // commit, after two people have checked the local production build; a
  // drill build (NEXT_PUBLIC_MOCK=1) keeps it and shows the MOCK banner
  // (docs/RUNBOOK.md, G4).
  robots: { index: false, follow: false, nocache: true },
};

export const viewport = { width: "device-width", initialScale: 1 };

export default function RootLayout({ children }) {
  return (
    <html lang="en-GB" className={inter.variable}>
      <body>
        <PreReleaseBanner />
        {/* policyengine.org's header and menu, with its mobile menu
            (utils/siteNav.js; siteHeader.css for the rest of its look) */}
        <PolicyEngineShell
          country="uk"
          showFooter={false}
          headerProps={{ navItems: SITE_NAV_ITEMS, styles: SITE_HEADER_STYLES }}
        >
          {children}
          <PolicyEngineFooter />
        </PolicyEngineShell>
      </body>
    </html>
  );
}

import PolicyEngineFooter from "../src/components/PolicyEngineFooter";
import PolicyEngineHeader from "../src/components/PolicyEngineHeader";
import PreReleaseBanner from "../src/components/PreReleaseBanner";

import "./globals.css";

export const metadata = {
  title: "Energy price cap, January to March 2027 (pre-release template) | PolicyEngine",
  description:
    "Pre-release template of the PolicyEngine dashboard for the January to March 2027 energy price cap. All figures are placeholders.",
  // Pre-release template: never indexed. Remove only at G4 on the day, after
  // checking the preview behind the login (docs/RUNBOOK.md).
  robots: { index: false, follow: false, nocache: true },
};

export default function RootLayout({ children }) {
  return (
    <html lang="en-GB">
      <body>
        <PreReleaseBanner />
        <PolicyEngineHeader />
        {children}
        <PolicyEngineFooter />
      </body>
    </html>
  );
}

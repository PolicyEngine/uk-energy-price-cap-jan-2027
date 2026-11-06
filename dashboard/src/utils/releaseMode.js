// Release mode, fixed at build time. A drill build sets NEXT_PUBLIC_MOCK=1:
// the banner, the page title and every download then say MOCK, so a mock
// figure cannot leave the machine looking real (docs/RUNBOOK.md, G4).
export function isMock(env = process.env.NEXT_PUBLIC_MOCK) {
  return env === "1";
}

export const MOCK_BANNER_TEXT = "MOCK — drill build with mock figures. Not an estimate of the January to March 2027 energy price cap.";
export const TEMPLATE_BANNER_TEXT =
  "Pre-release template — placeholder figures. Not an estimate of the January to March 2027 energy price cap.";

export function bannerText(mock = isMock()) {
  return mock ? MOCK_BANNER_TEXT : TEMPLATE_BANNER_TEXT;
}

export function pageTitle(title, mock = isMock()) {
  return mock ? `MOCK: ${title}` : title;
}

/** File name for a download; MOCK- in front in a drill build. */
export function downloadName(name, mock = isMock()) {
  return mock ? `MOCK-${name}` : name;
}

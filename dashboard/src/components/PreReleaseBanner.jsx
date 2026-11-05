export const BANNER_TEXT =
  "Pre-release template — placeholder figures. Not an estimate of the January to March 2027 energy price cap.";

export default function PreReleaseBanner() {
  return (
    <div className="pre-release-banner" role="status" data-testid="pre-release-banner">
      {BANNER_TEXT}
    </div>
  );
}

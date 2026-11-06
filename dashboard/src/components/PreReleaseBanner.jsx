import { bannerText } from "../utils/releaseMode";

export const BANNER_TEXT = bannerText(false);

export default function PreReleaseBanner({ text = bannerText() }) {
  return (
    <div className="pre-release-banner" role="status" data-testid="pre-release-banner">
      {text}
    </div>
  );
}

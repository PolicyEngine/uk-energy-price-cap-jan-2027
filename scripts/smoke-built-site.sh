#!/usr/bin/env bash
# Check that a served production build answers the page, each tab's
# address, the data files and logos under the base path with HTTP 200,
# sends X-Robots-Tag noindex, and shows the banner.
#
# Usage: scripts/smoke-built-site.sh [site URL]
#   default http://127.0.0.1:4871/uk/energy-price-cap-jan-2027
# MOCK=1 also requires the MOCK banner (drill builds).
set -euo pipefail

SITE="${1:-http://127.0.0.1:4871/uk/energy-price-cap-jan-2027}"
SITE="${SITE%/}"
TABS=("" "?tab=cap" "?tab=bills" "?tab=bills&sub=groups" "?tab=support" "?tab=household" "?tab=policies" "?tab=methodology")
FILES=("data/results.json" "data/manifest.json" "assets/logos/policyengine-teal.png" "assets/logos/policyengine-white.svg")

failures=0
body=$(mktemp)
headers=$(mktemp)
trap 'rm -f "$body" "$headers"' EXIT

fetch() {
  curl --silent --show-error --max-time 60 --dump-header "$headers" \
    --output "$body" --write-out '%{http_code}' "$1" || echo "000"
}

for tab in "${TABS[@]}"; do
  url="$SITE/$tab"
  [ -z "$tab" ] && url="$SITE"
  code=$(fetch "$url")
  if [ "$code" != 200 ]; then
    echo "FAIL $url: HTTP $code"; failures=$((failures + 1)); continue
  fi
  if ! grep -qi '^x-robots-tag: noindex, nofollow' "$headers"; then
    echo "FAIL $url: no X-Robots-Tag noindex"; failures=$((failures + 1))
  fi
  if ! grep -q 'name="robots" content="noindex' "$body"; then
    echo "FAIL $url: no meta robots noindex"; failures=$((failures + 1))
  fi
  if ! grep -q 'data-testid="pre-release-banner"' "$body"; then
    echo "FAIL $url: no banner"; failures=$((failures + 1))
  fi
  if [ "${MOCK:-}" = 1 ] && ! grep -q 'MOCK' "$body"; then
    echo "FAIL $url: no MOCK banner"; failures=$((failures + 1))
  fi
  echo "ok   $url"
done

for file in "${FILES[@]}"; do
  url="$SITE/$file"
  code=$(fetch "$url")
  if [ "$code" != 200 ]; then
    echo "FAIL $url: HTTP $code"; failures=$((failures + 1))
  else
    echo "ok   $url"
  fi
done

echo "$failures failure(s)"
[ "$failures" = 0 ]

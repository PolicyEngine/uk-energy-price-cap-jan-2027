"""Certified engine and dataset pairs the post scripts accept.

Each entry is a ``policyengine`` release and the policyengine-uk, -core and
Microcosm UK build it certifies. The scripts pick the entry for the installed
``policyengine`` and refuse anything else, so a run is always on a certified
pair. 6.20.2 is the pair behind the 19 November 2026 Cornwall Insight post
(kept to reproduce it); 6.20.3 is the pair for the Ofgem post.
"""

import os
from importlib import metadata
from pathlib import Path

DATASET_REPO = "policyengine/populace-uk-private"
RELEASE = "releases/microcosm-uk-2024-25-national"
FILE = "microcosm_uk_2024_25.h5"

BUNDLES = {
    "6.20.2": {
        "engine": {"policyengine-uk": "2.177.7", "policyengine-core": "3.34.10"},
        "build": "uk-frs-calibration-attempt-20261115T104657Z-fcfac709",
        "sha256": "301d2fe5e7805c5a6242b37843cb118445aefd59a0593833362ab5a6e2f9ba90",
        "revision": "ad84c0602ed28f694ef52662eb9b063779e4e923",
    },
    "6.20.3": {
        "engine": {"policyengine-uk": "2.179.2", "policyengine-core": "3.34.10"},
        "build": "uk-frs-calibration-attempt-20261122T100732Z-b891aa69",
        "sha256": "ae116bc3cff798fe68df253083f0b26d779e02a0a818ee68df7d29fbc557165a",
        "revision": "a80a4bf70ab4ffeac77357fe0633d3cee4ce7401",
    },
}


def installed_bundle():
    """(policyengine version, bundle) for the installed packages; raises if
    the installed engine is not the pair that release certifies."""
    versions = {
        p: metadata.version(p)
        for p in ("policyengine", "policyengine-uk", "policyengine-core")
    }
    pe = versions["policyengine"]
    if pe not in BUNDLES:
        raise SystemExit(f"policyengine {pe} is not a certified pair here: {sorted(BUNDLES)}")
    bundle = BUNDLES[pe]
    for package, version in bundle["engine"].items():
        if versions[package] != version:
            raise SystemExit(
                f"policyengine {pe} certifies {package} {version}, found {versions[package]}"
            )
    return versions, bundle


def dataset_path(bundle):
    """Local path of the bundle's dataset: MICROCOSM_DATASET if set, else
    data/<release>/<build>/<file> under MICROCOSM_ROOT (default: post/data)."""
    if os.environ.get("MICROCOSM_DATASET"):
        return Path(os.environ["MICROCOSM_DATASET"])
    root = Path(os.environ.get("MICROCOSM_ROOT", Path(__file__).parent / "data"))
    return root / RELEASE / bundle["build"] / FILE

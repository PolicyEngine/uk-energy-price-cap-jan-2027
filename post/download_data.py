"""Fetch the Microcosm UK build that the installed policyengine certifies.

The file is in a private Hugging Face dataset; the download reads the token
from HUGGING_FACE_TOKEN (or HF_TOKEN). run_cap.py checks its SHA-256.
"""

import os
import shutil

from huggingface_hub import hf_hub_download

from bundles import DATASET_REPO, FILE, RELEASE, dataset_path, installed_bundle

_, bundle = installed_bundle()
dest = dataset_path(bundle)
if dest.exists():
    print(f"{dest} already there")
else:
    token = os.environ.get("HUGGING_FACE_TOKEN") or os.environ.get("HF_TOKEN")
    source = hf_hub_download(
        DATASET_REPO,
        f"{RELEASE}/{bundle['build']}/{FILE}",
        repo_type="dataset",
        revision=bundle["revision"],
        token=token,
    )
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, dest)
    print(dest)

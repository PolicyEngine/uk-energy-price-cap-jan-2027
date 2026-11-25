"""Check that run_cap.py reproduces the 19 November 2026 post.

Compares the Cornwall Insight scenario of a policyengine 6.20.2 run with the
published results of that post (uk-energy-price-cap-2027/results/results.json),
key by key, and exits non-zero on any difference beyond floating-point noise.

    uv run --no-project --with 'policyengine[uk]==6.20.2' python run_cap.py
    uv run python check_reproduction.py results/results-6.20.2.json <published results.json>
"""

import json
import math
import sys

TOL = 1e-9


def walk(a, b, path, bad):
    if isinstance(a, dict):
        for k in a:
            if k == "q1_change_typical_split":  # null placeholder in the old script
                continue
            if k not in b:
                bad.append(f"{path}.{k}: missing in the new run")
                continue
            walk(a[k], b[k], f"{path}.{k}", bad)
    elif isinstance(a, list):
        if len(a) != len(b):
            bad.append(f"{path}: length {len(a)} against {len(b)}")
        for i, (x, y) in enumerate(zip(a, b)):
            walk(x, y, f"{path}[{i}]", bad)
    elif isinstance(a, (int, float)) and not isinstance(a, bool):
        if not math.isclose(a, b, rel_tol=TOL, abs_tol=TOL):
            bad.append(f"{path}: published {a} against {b}")
    elif a != b:
        bad.append(f"{path}: published {a!r} against {b!r}")


def main(new_path, published_path):
    new, pub = json.load(open(new_path)), json.load(open(published_path))
    sc = new["scenarios"]["cornwall"]
    bad = []
    walk(pub["versions"], new["versions"], "versions", bad)
    walk(pub["dataset"], new["dataset"], "dataset", bad)
    walk(pub["gb"], sc["gb"], "gb", bad)
    walk(pub["deciles"], sc["deciles"], "deciles", bad)
    walk(pub["decile_values_present"], new["decile_values_present"], "decile_values_present", bad)
    for name, ex in pub["examples"].items():
        for label in ("oct", "jan"):
            walk(ex[label], {k: sc["examples"][name][label][k] for k in ex[label]}, f"examples.{name}.{label}", bad)
        walk(ex["change"], sc["examples"][name]["change"], f"examples.{name}.change", bad)
        walk(ex["change_pct"], sc["examples"][name]["change_pct"], f"examples.{name}.change_pct", bad)
    pi, ni = pub["inputs"], sc["inputs"]
    pairs = {
        "oct_typical_bill": "oct_typical_bill", "oct_typical_total": "oct_typical_total",
        "jan_forecast_bill": "jan_typical_bill", "jan_forecast_total": "jan_typical_total",
        "factor": "factor", "jan_standing_p_per_day_backed_out": "jan_standing_p_per_day",
    }
    for old, newk in pairs.items():
        walk(pi[old], ni[newk], f"inputs.{old}", bad)
    walk(pi["to_q4"], new["to_q4"], "inputs.to_q4", bad)
    if bad:
        print(f"{len(bad)} differences:")
        print("\n".join(bad[:50]))
        sys.exit(1)
    print(f"reproduced: every published figure matches ({len(pub['deciles'])} deciles, "
          f"{len(pub['gb'])} Great Britain figures, {len(pub['examples'])} examples, inputs)")


if __name__ == "__main__":
    main(*sys.argv[1:3])

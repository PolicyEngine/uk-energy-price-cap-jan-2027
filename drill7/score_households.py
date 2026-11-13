"""Score the drill 7 specimen households (T40_documents.md s1-s4).

Exact Decimal arithmetic; each bill summed in pence unrounded, rounded once
to the penny, half up. Usage: python score_households.py INPUTS SHA OUT.
"""

import csv
import json
import sys
from decimal import ROUND_HALF_UP, Decimal

D = Decimal
DAYS = D(365)


def bill(h, r):
    """Annual bill in pounds, rounded once to the penny, half up."""
    if h["method"] == "economy_7_direct_debit":
        p = D(h["day"]) * D(r["day"]) + D(h["night"]) * D(r["night"])
        p += DAYS * D(r["elec_sc"])
    else:
        p = D(h["elec"]) * D(r["elec_unit"]) + DAYS * D(r["elec_sc"])
    if D(h["gas"]) > 0:
        p += D(h["gas"]) * D(r["gas_unit"]) + DAYS * D(r["gas_sc"])
    return (p / 100).quantize(D("0.01"), rounding=ROUND_HALF_UP)


def support(h, s):
    parts = []
    c, b = h["country"], h["band"]
    if c in s["hep_first"]["countries"] and b in s["hep_first"]["bands"]:
        parts.append(("HEP first Jan 2027", D(s["hep_first"]["amount"])))
    if c in s["devolved"]["countries"] and b in s["devolved"]["bands"]:
        parts.append((f"{c} £100 Jan 2027", D(s["devolved"]["amount"])))
    if h["benefit"] and c in s["whd"]["countries"]:
        parts.append(("WHD", D(s["whd"]["amount"])))
        parts.append(("WHD top-up", D(s["whd_top_up"]["amount"])))
    w = s["wfp"]
    if h["oldest"] >= w["higher_age"]:
        parts.append(("WFP 80+", D(w["higher"])))
    elif h["oldest"] >= w["lower_age"]:
        parts.append(("WFP 66-79", D(w["lower"])))
    second = D(0)
    hs = s["hep_second"]
    if c in hs["countries"] and b in hs["bands"]:
        second = D(hs["amount"])
    return parts, second


def main(inputs, sha, out, before="oct_dec_2026", after="jan_mar_2027"):
    data = json.load(open(inputs))
    rows = []
    for h in data["households"]:
        row = {"household_id": h["id"], "scoring_sha": sha}
        if h.get("out_of_scope"):
            row.update(in_scope="no", notes=h["out_of_scope"])
            rows.append(row)
            continue
        r0 = data["rates"][before][h["method"]]
        r1 = data["rates"][after][h["method"]]
        b0, b1 = bill(h, r0), bill(h, r1)
        parts, second = support(h, data["support"])
        sup = sum((v for _, v in parts), D(0))
        change = b1 - b0
        note = "support: " + (
            " + ".join(f"{k} £{v}" for k, v in parts) if parts else "none"
        )
        note += h.get("note", "")
        row.update(
            in_scope="yes",
            bill_oct_dec_2026=f"{b0:.2f}",
            bill_jan_mar_2027=f"{b1:.2f}",
            annual_change=f"{change:.2f}",
            winter_2026_27_support=f"{sup:.2f}",
            net_change_after_winter_support=f"{change - sup:.2f}",
            second_hep_apr_2027=f"{second:.2f}",
            notes=note,
        )
        rows.append(row)
    fields = [
        "household_id", "scoring_sha", "in_scope", "bill_oct_dec_2026",
        "bill_jan_mar_2027", "annual_change", "winter_2026_27_support",
        "net_change_after_winter_support", "second_hep_apr_2027", "notes",
    ]
    with open(out, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for row in rows:
            w.writerow({k: row.get(k, "") for k in fields})


if __name__ == "__main__":
    main(*sys.argv[1:4])

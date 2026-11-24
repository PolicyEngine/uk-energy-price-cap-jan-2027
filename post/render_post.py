"""Render the Ofgem post from results: every figure the post quotes comes from
run_cap.py's output; nothing is typed into the article by hand.

    uv run python render_post.py --app-v2 ../../policyengine-app-v2

writes into the app-v2 checkout:
  app/src/data/posts/articles/uk-energy-price-cap-january-2027.md
  app/src/data/posts/posts.json            (this post's entry, added or updated)
  website/src/components/home/FeaturedResearchBanner.tsx  (the Latest research card)

Until Ofgem's block in inputs.json is filled and run_cap.py rerun, every Ofgem
figure renders as a visible placeholder (**[Ofgem: name]**) in prose and as
null in chart data. --scenario cornwall renders the same template on Cornwall
Insight's forecast instead, to check the wiring against the 19 November post.
"""

import argparse
import json
import re
from decimal import ROUND_HALF_UP, Decimal
from pathlib import Path

HERE = Path(__file__).parent
SLUG = "uk-energy-price-cap-january-2027"
ARTICLE = f"app/src/data/posts/articles/{SLUG}.md"
POSTS = "app/src/data/posts/posts.json"
BANNER = "website/src/components/home/FeaturedResearchBanner.tsx"
FORECAST_SLUG = "uk-energy-price-cap-january-2027-forecast"
MINUS = "−"


class Missing:
    """A figure that needs Ofgem's cap."""

    def __init__(self, name):
        self.name = name


def rnd(x, places=0):
    q = Decimal(1).scaleb(-places)
    return Decimal(repr(float(x))).quantize(q, rounding=ROUND_HALF_UP)


def num(x, places=0, sep=True):
    d = rnd(x, places)
    s = f"{abs(d):,.{places}f}" if sep else f"{abs(d):.{places}f}"
    return (MINUS if d < 0 else "") + s


def signed(s, x, places=0):
    return ("+" if rnd(x, places) > 0 else (MINUS if rnd(x, places) < 0 else "")) + s.lstrip(MINUS)


FMT = {
    "gbp": lambda x: "£" + num(x).lstrip(MINUS) if x >= 0 else MINUS + "£" + num(x).lstrip(MINUS),
    "sgbp": lambda x: signed("£" + num(abs(x)), x),
    "pct1": lambda x: num(100 * x, 1) + "%",
    "spct1": lambda x: signed(num(100 * abs(x), 1) + "%", x, 3),
    "pct0": lambda x: num(100 * x) + "%",
    "pct2": lambda x: num(100 * x, 2) + "%",
    "agbp": lambda x: "£" + num(abs(x)),
    "npct1": lambda x: float(rnd(100 * x, 1)),
    "p2": lambda x: num(x, 2),
    "m1": lambda x: num(x, 1) + " million",
    "int": lambda x: num(x),
    "n0": lambda x: float(rnd(x)),
    "n1": lambda x: float(rnd(x, 1)),
    "n3": lambda x: float(rnd(x, 3)),
}


def fmt(value, kind):
    if isinstance(value, Missing):
        return "null" if kind.startswith("n") else f"**[Ofgem: {value.name}]**"
    if isinstance(value, str):
        return value
    out = FMT[kind](value)
    return json.dumps(out) if kind.startswith("n") else out


def word(value, pos, neg, name):
    if isinstance(value, Missing):
        return f"**[Ofgem: {pos} or {neg}]**"
    return pos if value >= 0 else neg


def figures(res, key, previous):
    """The flat set of named figures the template uses."""
    sc = res["scenarios"].get(key)
    fc = res["scenarios"]["cornwall"]  # forecast on the same engine and data
    base = fc  # October figures do not depend on the January scenario

    def g(path, src=None):
        src = sc if src is None else src
        if src is None:
            return Missing(path)
        v = src
        for p in path.split("."):
            v = v[int(p)] if isinstance(v, list) else v[p]
        return v

    def diff(a, b):
        return Missing("difference") if isinstance(a, Missing) or isinstance(b, Missing) else a - b

    F = {}
    F["ofgem_date"] = g("announced_on") if sc and sc.get("announced_on") else Missing("announcement date")
    F["jan_total"] = g("typical_bill_announced")
    F["oct_total"] = res["october"]["typical_bill_announced"]
    F["fc_total"] = fc["typical_bill_announced"]
    F["jan_change"] = diff(F["jan_total"], F["oct_total"])
    F["jan_change_pct"] = Missing("change") if isinstance(F["jan_total"], Missing) else F["jan_total"] / F["oct_total"] - 1
    F["jan_vs_fc"] = diff(F["jan_total"], F["fc_total"])
    F["jan_vs_fc_abs"] = Missing("difference") if isinstance(F["jan_vs_fc"], Missing) else abs(F["jan_vs_fc"])
    F["dir_change"] = word(F["jan_change"], "rise", "fall", "jan_change")
    F["dir_vs_fc"] = word(F["jan_vs_fc"], "above", "below", "jan_vs_fc")
    F["dir_more_less"] = word(F["jan_change"], "more", "less", "jan_change")
    F["dir_vs_fc_more_less"] = word(F["jan_vs_fc"], "more", "less", "jan_vs_fc")

    for f, short in (("electricity", "e"), ("gas", "g")):
        F[f"oct_unit_{short}"] = res["october"]["rates"]["unit"][f]
        F[f"oct_standing_{short}"] = res["october"]["rates"]["standing"][f]
        F[f"oct_bill_{short}"] = base["inputs"]["oct_typical_bill"][f]
        for label, src in (("jan", sc), ("fc", fc)):
            F[f"{label}_unit_{short}"] = g(f"inputs.jan_unit_p_per_kwh.{f}", src)
            F[f"{label}_standing_{short}"] = g(f"inputs.jan_standing_p_per_day.{f}", src)
            F[f"{label}_bill_{short}"] = g(f"inputs.jan_typical_bill.{f}", src)
            F[f"{label}_unit_pct_{short}"] = g(f"inputs.unit_change_pct.{f}", src)
            F[f"{label}_standing_pct_{short}"] = g(f"inputs.standing_change_pct.{f}", src)
            F[f"{label}_bill_pct_{short}"] = g(f"inputs.typical_fuel_change_pct.{f}", src)
            F[f"{label}_fuel_change_{short}"] = g(f"inputs.typical_fuel_change.{f}", src)
        F[f"q1_share_{short}"] = fc["inputs"]["q1_share"][f]
    F["oct_bill_total"] = base["inputs"]["oct_typical_total"]
    F["jan_bill_total"] = g("inputs.jan_typical_total")
    F["fc_bill_total"] = fc["inputs"]["jan_typical_total"]
    F["jan_bill_total_pct"] = Missing("change") if sc is None else sc["inputs"]["jan_typical_total"] / F["oct_bill_total"] - 1
    F["jan_rate_change"] = diff(F["jan_bill_total"], F["oct_bill_total"])
    F["gas_share"] = g("inputs.gas_share_of_typical_change")

    ex_names = {"low": "low_dual_fuel_half_typical", "typ": "typical_dual_fuel",
                "high": "high_dual_fuel_double_typical", "eo": "electric_only_typical_electricity"}
    for short, name in ex_names.items():
        for part in ("electricity", "gas", "total", "standing", "unit"):
            F[f"ex_{short}_oct_{part}"] = base["examples"][name]["oct"][part]
            F[f"ex_{short}_jan_{part}"] = g(f"examples.{name}.jan.{part}")
        for part in ("change", "change_pct", "q1_change", "standing_share_jan"):
            F[f"ex_{short}_{part}"] = g(f"examples.{name}.{part}")
    for f, short in (("electricity", "e"), ("gas", "g")):
        F[f"half_pct_{short}"] = g(f"examples.low_dual_fuel_half_typical.jan.fuel_change_pct.{f}")
        F[f"typ_pct_{short}"] = g(f"examples.typical_dual_fuel.jan.fuel_change_pct.{f}")
    # Direction of the standing-charge limitation: if the half-use rise is
    # below the typical rise, one factor per fuel overstates the rise for low
    # users.
    lo = (Missing("x") if sc is None else
          sc["examples"]["low_dual_fuel_half_typical"]["jan"]["fuel_change_pct"]["electricity"]
          - sc["examples"]["typical_dual_fuel"]["jan"]["fuel_change_pct"]["electricity"])
    F["sc_low"] = word(Missing("x") if isinstance(lo, Missing) else -lo, "overstate", "understate", "")
    F["sc_high"] = word(Missing("x") if isinstance(lo, Missing) else -lo, "understate", "overstate", "")
    F["sc_low_dir"] = word(Missing("x") if isinstance(lo, Missing) else -lo, "lower", "higher", "")
    F["eo_vs_gas"] = word(diff(F["jan_unit_pct_g"], F["jan_unit_pct_e"]), "less", "more", "")

    for label, src in (("", base),):
        gb = src["gb"]
        F["mean_before"] = gb["mean_before"]
        F["dual_mean_before"] = gb["dual_mean_before"]
        F["dual_median_before"] = gb["dual_median_before"]
        F["elec_only_mean_before"] = gb["elec_only_mean_before"]
        F["n_dual"] = gb["households_dual_fuel_m"]
        F["n_elec_only"] = gb["households_electric_only_m"]
        F["share_before"] = gb["share_of_income_before"]
        F["over10_before"] = gb["spend_over_10pct_income_before_m"]
        F["zero_income"] = gb["net_income_nonpositive_m"]
        F["d1_share_before"] = src["deciles"][0]["share_before"]
        F["d10_share_before"] = src["deciles"][9]["share_before"]
    for label, src in (("", sc), ("fc_", fc)):
        F[f"{label}mean_after"] = g("gb.mean_after", src)
        F[f"{label}mean_change"] = g("gb.mean_change", src)
        F[f"{label}dual_mean_change"] = g("gb.dual_mean_change", src)
        F[f"{label}elec_only_mean_change"] = g("gb.elec_only_mean_change", src)
        F[f"{label}share_after"] = g("gb.share_of_income_after", src)
        F[f"{label}over10_after"] = g("gb.spend_over_10pct_income_after_m", src)
        F[f"{label}change_total_bn"] = g("gb.change_total_bn", src)
        for d in (1, 10):
            F[f"{label}d{d}_change"] = g(f"deciles.{d - 1}.mean_change", src)
            F[f"{label}d{d}_share_after"] = g(f"deciles.{d - 1}.share_after", src)
    F["mean_vs_fc"] = diff(F["mean_change"], F["fc_mean_change"])
    F["over10_vs_fc"] = diff(F["over10_after"], F["fc_over10_after"])
    F["d1_vs_fc"] = diff(F["d1_change"], F["fc_d1_change"])
    F["d10_vs_fc"] = diff(F["d10_change"], F["fc_d10_change"])
    F["jan_unit_vs_fc_e"] = diff(F["jan_unit_e"], F["fc_unit_e"])
    F["jan_unit_vs_fc_g"] = diff(F["jan_unit_g"], F["fc_unit_g"])
    F["jan_standing_vs_fc_e"] = diff(F["jan_standing_e"], F["fc_standing_e"])
    F["jan_standing_vs_fc_g"] = diff(F["jan_standing_g"], F["fc_standing_g"])

    v = res["versions"]
    F["pe_version"] = v["policyengine"]
    F["pe_uk_version"] = v["policyengine-uk"]
    F["build_short"] = res["dataset"]["build"][-8:]
    if previous:
        pf = previous["scenarios"]["cornwall"]
        F["prev_pe_version"] = previous["versions"]["policyengine"]
        F["prev_build_short"] = previous["dataset"]["build"][-8:]
        F["prev_mean_change"] = pf["gb"]["mean_change"]
        F["prev_d1_share_before"] = pf["deciles"][0]["share_before"]
        F["prev_over10_before"] = pf["gb"]["spend_over_10pct_income_before_m"]
    else:
        for k in ("prev_pe_version", "prev_build_short", "prev_mean_change",
                  "prev_d1_share_before", "prev_over10_before"):
            F[k] = Missing("earlier run: pass --previous")
    F["_sc"], F["_fc"], F["_base"], F["_res"] = sc, fc, base, res
    return F


# ---------------------------------------------------------------- blocks


def cell(v, kind):
    return fmt(v, kind)


def two(a, b, kind="gbp"):
    return f"{fmt(a, kind)} to {fmt(b, kind)}"


def blocks(F, kind_label):
    sc, fc, base, res = F["_sc"], F["_fc"], F["_base"], F["_res"]
    B = {}
    jan_hist = "null" if isinstance(F["jan_total"], Missing) else fmt(F["jan_total"], "n0")
    rows = [f'    {{ "quarter": "{q["quarter"]}", "ofgem": {q["at_current_tdcv"]} }}' for q in res["history"]]
    rows.append(f'    {{ "quarter": "Jan–Mar 2027", "ofgem": {jan_hist} }}')
    B["fig1_data"] = ",\n".join(rows)

    t1 = []
    for q in res["history"]:
        t1.append(f"| {q['label']} | {num(q['announced'])} | {q['tdcv']} | {num(q['at_current_tdcv'])} |")
    t1.append(f"| January to March 2027 | {fmt(F['jan_total'], 'int')} ({kind_label}) | 2,500 and 9,500 | {fmt(F['jan_total'], 'int')} |")
    B["table1_rows"] = "\n".join(t1)

    def r(label, o, j, f, ch, kind, chkind="spct1"):
        return f"| {label} | {fmt(o, kind)} | {fmt(j, kind)} | {fmt(ch, chkind)} | {fmt(f, kind)} |"

    B["table2_rows"] = "\n".join([
        r("Electricity unit rate (pence per kWh)", F["oct_unit_e"], F["jan_unit_e"], F["fc_unit_e"], F["jan_unit_pct_e"], "p2"),
        r("Electricity standing charge (pence per day)", F["oct_standing_e"], F["jan_standing_e"], F["fc_standing_e"], F["jan_standing_pct_e"], "p2"),
        r("Gas unit rate (pence per kWh)", F["oct_unit_g"], F["jan_unit_g"], F["fc_unit_g"], F["jan_unit_pct_g"], "p2"),
        r("Gas standing charge (pence per day)", F["oct_standing_g"], F["jan_standing_g"], F["fc_standing_g"], F["jan_standing_pct_g"], "p2"),
        r("Typical electricity bill (£ a year)", F["oct_bill_e"], F["jan_bill_e"], F["fc_bill_e"], F["jan_bill_pct_e"], "int"),
        r("Typical gas bill (£ a year)", F["oct_bill_g"], F["jan_bill_g"], F["fc_bill_g"], F["jan_bill_pct_g"], "int"),
        f"| **Typical dual-fuel bill (£ a year)** | **{fmt(F['oct_total'], 'int')}** | **{fmt(F['jan_total'], 'int')}** "
        f"| **{fmt(F['jan_change_pct'], 'spct1')}** | **{fmt(F['fc_total'], 'int')}** |",
    ])

    def ex(short, kind):
        return F[f"ex_{short}_jan_{kind}"]

    B["fig3_data"] = ",\n".join(
        f'    {{ "household": "{name}", "oct": {fmt(F[f"ex_{s}_oct_total"], "n0")}, "jan": {fmt(ex(s, "total"), "n0")} }}'
        for s, name in (("low", "Low use"), ("typ", "Typical use"), ("high", "High use"), ("eo", "Electricity only"))
    )
    fig4 = []
    for s, name in (("low", "Low use"), ("typ", "Typical use"), ("high", "High use")):
        fig4.append(f'    {{ "household": "{name}", "electricity": {fmt(ex(s, "electricity"), "n0")}, "gas": {fmt(ex(s, "gas"), "n0")} }}')
    fig4.append(f'    {{ "household": "Electricity only", "electricity": {fmt(ex("eo", "electricity"), "n0")} }}')
    B["fig4_data"] = ",\n".join(fig4)

    t3 = []
    for s, name in (("low", "Low use (half typical)"), ("typ", "Typical use"),
                    ("high", "High use (double typical)"), ("eo", "Electricity only, typical")):
        gas = "£0" if s == "eo" else two(F[f"ex_{s}_oct_gas"], ex(s, "gas"))
        t3.append(
            f"| {name} | {two(F[f'ex_{s}_oct_electricity'], ex(s, 'electricity'))} | {gas} "
            f"| {two(F[f'ex_{s}_oct_total'], ex(s, 'total'))} | {two(F[f'ex_{s}_oct_standing'], ex(s, 'standing'))} "
            f"| {two(F[f'ex_{s}_oct_unit'], ex(s, 'unit'))} | {fmt(F[f'ex_{s}_change'], 'sgbp')} ({fmt(F[f'ex_{s}_change_pct'], 'spct1')}) "
            f"| {fmt(F[f'ex_{s}_q1_change'], 'sgbp')} |"
        )
    B["table3_rows"] = "\n".join(t3)

    def dec(i, k, src):
        return Missing(f"decile {i + 1}") if src is None else src["deciles"][i][k]

    B["fig5_data"] = ",\n".join(
        f'    {{ "decile": "{i + 1}", "oct": {fmt(base["deciles"][i]["mean_before"], "n0")}, "jan": {fmt(dec(i, "mean_after", sc), "n0")} }}'
        for i in range(10))
    B["fig6_data"] = ",\n".join(
        f'    {{ "decile": "{i + 1}", "oct": {fmt(base["deciles"][i]["share_before"] * 100, "n3")}, '
        f'"jan": {"null" if sc is None else fmt(sc["deciles"][i]["share_after"] * 100, "n3")} }}'
        for i in range(10))
    B["fig7_data"] = ",\n".join(
        f'    {{ "decile": "{i + 1}", "change": {fmt(dec(i, "mean_change", sc), "n0")} }}' for i in range(10))
    B["fig8_data"] = ",\n".join(
        f'    {{ "decile": "{i + 1}", "forecast": {fmt(fc["deciles"][i]["mean_change"], "n0")}, '
        f'"ofgem": {fmt(dec(i, "mean_change", sc), "n0")} }}' for i in range(10))
    t4 = []
    for i in range(10):
        b = base["deciles"][i]
        name = {0: "1 (lowest)", 9: "10 (highest)"}.get(i, str(i + 1))
        t4.append(
            f"| {name} | {fmt(b['mean_net_income'], 'gbp')} | {fmt(b['mean_before'], 'gbp')} | {fmt(dec(i, 'mean_after', sc), 'gbp')} "
            f"| {fmt(dec(i, 'mean_change', sc), 'sgbp')} | {fmt(b['share_before'], 'pct1')} | {fmt(dec(i, 'share_after', sc), 'pct1')} |"
        )
    t4.append(f"| All | | {fmt(F['mean_before'], 'gbp')} | {fmt(F['mean_after'], 'gbp')} | {fmt(F['mean_change'], 'sgbp')} "
              f"| {fmt(F['share_before'], 'pct1')} | {fmt(F['share_after'], 'pct1')} |")
    B["table4_rows"] = "\n".join(t4)

    def rr(label, f, j, d, kind, dkind):
        return f"| {label} | {fmt(f, kind)} | {fmt(j, kind)} | {fmt(d, dkind)} |"

    B["table5_rows"] = "\n".join([
        rr("Typical dual-fuel bill (£ a year)", F["fc_total"], F["jan_total"], F["jan_vs_fc"], "int", "sgbp"),
        rr("Electricity unit rate (pence per kWh)", F["fc_unit_e"], F["jan_unit_e"], F["jan_unit_vs_fc_e"], "p2", "p2"),
        rr("Gas unit rate (pence per kWh)", F["fc_unit_g"], F["jan_unit_g"], F["jan_unit_vs_fc_g"], "p2", "p2"),
        rr("Change in the average household bill (£ a year)", F["fc_mean_change"], F["mean_change"], F["mean_vs_fc"], "sgbp", "sgbp"),
        rr("Change, lowest income decile (£ a year)", F["fc_d1_change"], F["d1_change"], F["d1_vs_fc"], "sgbp", "sgbp"),
        rr("Change, highest income decile (£ a year)", F["fc_d10_change"], F["d10_change"], F["d10_vs_fc"], "sgbp", "sgbp"),
        f"| Households spending over 10% of net income on energy (million) | {fmt(F['fc_over10_after'], 'n1')} "
        f"| {fmt(F['over10_after'], 'n1')} | {fmt(F['over10_vs_fc'], 'n1')} |".replace("null", "**[Ofgem]**"),
    ])
    return B


TOKEN = re.compile(r"\{\{\s*([a-z0-9_]+)(?::([a-z0-9]+))?\s*\}\}")


def render(template, F, B):
    def sub(m):
        name, kind = m.group(1), m.group(2)
        if name in B:
            return B[name]
        if name not in F:
            raise KeyError(f"template uses unknown figure {name}")
        return fmt(F[name], kind or "str") if kind else (
            F[name] if isinstance(F[name], str) else fmt(F[name], "str"))

    out = TOKEN.sub(sub, template)

    # app-v2's chart parser rejects null values but accepts an absent key, so
    # a figure still waiting for Ofgem is left out of the chart data.
    def drop_nulls(m):
        block = re.sub(r',\s*"[a-z_]+": null', "", m.group(0))
        return re.sub(r'"[a-z_]+": null,\s*', "", block)

    return re.sub(r"```chart\n.*?\n```", drop_nulls, out, flags=re.S)


FMT["str"] = lambda x: str(x)


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--results", type=Path, default=HERE / "results" / "results-6.20.3.json")
    parser.add_argument("--previous", type=Path, default=HERE / "results" / "results-6.20.2.json",
                        help="the run behind the 19 November post (for the methodology note)")
    parser.add_argument("--scenario", default="ofgem", choices=["ofgem", "cornwall"])
    parser.add_argument("--app-v2", type=Path, help="policyengine-app-v2 checkout to write into")
    parser.add_argument("--out", type=Path, help="write only the article here (e.g. a scratch file)")
    args = parser.parse_args()

    res = json.loads(args.results.read_text())
    previous = json.loads(args.previous.read_text()) if args.previous and args.previous.exists() else None
    F = figures(res, args.scenario, previous)
    kind_label = "Ofgem's cap" if args.scenario == "ofgem" else "Cornwall Insight forecast"
    B = blocks(F, kind_label)
    article = render((HERE / "template.md").read_text(), F, B)
    meta_text = render((HERE / "meta.json").read_text(), F, B)
    meta = json.loads(meta_text.replace("**[Ofgem:", "[Ofgem:").replace("]**", "]"))
    missing = sorted(set(re.findall(r"\*\*\[Ofgem: ([^\]]+)\]\*\*", article + json.dumps(meta, ensure_ascii=False))))
    print(f"{len(missing)} distinct Ofgem placeholders left" + (f": {', '.join(missing[:8])}…" if missing else ""))

    if args.out:
        args.out.write_text(article)
        print(args.out)
    if args.app_v2:
        (args.app_v2 / ARTICLE).write_text(article)
        # Text edit, not a JSON round trip, so the rest of posts.json keeps its
        # formatting: replace this post's entry if present, else add it first.
        posts_path = args.app_v2 / POSTS
        text = posts_path.read_text()
        entry = json.dumps(meta["post"], indent=2, ensure_ascii=False)
        # Inline string arrays, as prettier writes posts.json.
        entry = re.sub(r"\[\s*((?:\"[^\"]*\",?\s*)+)\]",
                       lambda m: "[" + ", ".join(re.findall(r"\"[^\"]*\"", m.group(1))) + "]", entry)
        entry = "\n".join("  " + line for line in entry.splitlines())
        pat = re.compile(r"  \{\n(?:(?!  \{\n).)*?\"filename\": \"%s\.md\".*?\n  \}" % SLUG, re.S)
        if pat.search(text):
            text = pat.sub(lambda m: entry, text, count=1)
        else:
            assert text.startswith("[\n"), "unexpected posts.json layout"
            text = "[\n" + entry + ",\n" + text[2:]
        json.loads(text)
        posts_path.write_text(text)
        banner_path = args.app_v2 / BANNER
        banner = banner_path.read_text()
        card = meta["card"]
        new = (f'  {{\n    href: "{card["href"]}",\n    title: "{card["title"]}",\n'
               f'    desc: "{card["desc"]}",\n  }},\n')
        # Replace this post's card if present, else the forecast post's card
        # (superseded by Ofgem's cap), else add it first.
        pat = re.compile(r"  \{\n    href: \"/uk/research/(%s|%s)\",\n.*?\n  \},\n" % (SLUG, FORECAST_SLUG), re.S)
        if pat.search(banner):
            banner = pat.sub(lambda m: new, banner, count=1)
        else:
            banner = banner.replace("const cards = [\n", "const cards = [\n" + new, 1)
        banner_path.write_text(banner)
        print(f"wrote {ARTICLE}, {POSTS}, {BANNER} in {args.app_v2}")


if __name__ == "__main__":
    main()

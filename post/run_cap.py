"""Energy price cap, January to March 2027: household bills by income decile.

Reads the cap levels from inputs.json and writes one results file with every
figure the post quotes, for each January scenario whose inputs are filled:
Cornwall Insight's forecast (always) and Ofgem's cap (once its block in
inputs.json is filled in). All scenarios come from one simulation, so the
forecast and the actual cap are compared on the same engine and data.

    uv run python run_cap.py                  # writes results/results-<policyengine version>.json

Method (as in the 19 November 2026 post, uk-energy-price-cap-2027/run_cap.py):
1. Each household's fiscal 2026-27 electricity and gas spend from the model,
   restated at October to December 2026 prices with the engine's own indices
   (2026Q4 quarterly level over the fiscal-year level), fuel by fuel.
2. The engine's indices price electricity at the 5% energy input VAT basis
   (energy_prices/embedded_electricity_vat.yaml); domestic electricity in Great
   Britain is zero-rated from 1 October 2026, so electricity spend is divided
   by 1.05. Ofgem's rates carry 0% VAT on electricity and 5% on gas.
3. January bill = October bill x a factor per fuel: the January typical bill
   for that fuel over the typical bill at Ofgem's October rates (typical
   consumption 2,500 kWh electricity, 9,500 kWh gas).
4. Great Britain only (Northern Ireland is outside the Ofgem cap). Static:
   households do not change how much they use.
Income shares are decile totals: spend over HBAI net income before housing
costs (hbai_household_net_income), the income that ranks the deciles.
"""

import argparse
import hashlib
import json
import os
import sys
import time
from pathlib import Path

import numpy as np

from bundles import dataset_path, installed_bundle

HERE = Path(__file__).parent
YEAR = 2026
ENERGY_INPUT_VAT = 0.05
FUELS = ("electricity", "gas")
# Household examples: arithmetic on published rates, not model output.
EXAMPLES = {
    "low_dual_fuel_half_typical": {"electricity": 0.5, "gas": 0.5},
    "typical_dual_fuel": {"electricity": 1, "gas": 1},
    "high_dual_fuel_double_typical": {"electricity": 2, "gas": 2},
    "electric_only_typical_electricity": {"electricity": 1, "gas": 0},
}
# Shared heavy-run lock: one line, "<pid> <project> <job>", as the other
# PolicyEngine UK scripts on this machine use it.
LOCK = Path("/tmp/pe-heavy.lock")
# The scenario's typical bill from its rates must match its headline to this.
HEADLINE_TOLERANCE = 1.5


# ---------------------------------------------------------------- inputs


def scenario_is_filled(s):
    needed = [s["unit_p_per_kwh"][f] for f in FUELS]
    needed += [s["standing_p_per_day"][f] for f in FUELS]
    needed.append(s["typical_bill_announced"])
    if all(v is None for v in needed):
        return False
    missing = [k for k, v in zip(
        ["unit electricity", "unit gas", "standing electricity", "standing gas", "typical_bill_announced"],
        needed) if v is None]
    if missing:
        raise SystemExit(f"{s['label']}: inputs partly filled, missing {missing}")
    return True


def bill(unit, standing, kwh, days):
    """Annual bill in pounds from p/kWh, p/day and kWh."""
    return (kwh * unit + days * standing) / 100


def resolve_rates(cfg, s):
    """Unit rates, standing charges and typical bill per fuel for a January
    scenario. Where a source rounds standing charges to the penny (Cornwall
    Insight), they are backed out of its per-fuel typical bills so the typical
    bill reproduces exactly."""
    tdcv, days = cfg["typical_consumption_kwh"], cfg["days_in_year"]
    unit = dict(s["unit_p_per_kwh"])
    stated = s.get("typical_bill_by_fuel") or {}
    if s.get("standing_rounded_to_penny"):
        standing = {f: (stated[f] * 100 - tdcv[f] * unit[f]) / days for f in FUELS}
    else:
        standing = dict(s["standing_p_per_day"])
    typical = {f: bill(unit[f], standing[f], tdcv[f], days) for f in FUELS}
    for f in FUELS:
        if stated.get(f) is not None and abs(stated[f] - typical[f]) > HEADLINE_TOLERANCE:
            raise SystemExit(
                f"{s['label']}: {f} typical bill from rates £{typical[f]:.2f} "
                f"against stated £{stated[f]:.2f}; check the inputs"
            )
        if stated.get(f) is not None:
            typical[f] = stated[f]
    total = sum(typical.values())
    if abs(total - s["typical_bill_announced"]) > HEADLINE_TOLERANCE:
        raise SystemExit(
            f"{s['label']}: typical bill from rates £{total:.2f} against headline "
            f"£{s['typical_bill_announced']}; check the inputs"
        )
    return {"unit": unit, "standing": standing, "typical": typical}


def rate_arithmetic(cfg, oct_rates, jan, q1_share):
    """Everything the post computes from published rates alone: Table 2,
    Table 3, Figures 2 to 4 and the January to March changes."""
    tdcv, days, q1_days = cfg["typical_consumption_kwh"], cfg["days_in_year"], cfg["days_in_january_to_march"]

    def parts(rates, f, kwh):
        if kwh == 0:
            return {"standing": 0.0, "unit": 0.0, "total": 0.0}
        s = days * rates["standing"][f] / 100
        u = kwh * rates["unit"][f] / 100
        return {"standing": s, "unit": u, "total": s + u}

    examples = {}
    for name, scale in EXAMPLES.items():
        kwh = {f: tdcv[f] * scale[f] for f in FUELS}
        row = {"kwh": kwh}
        for label, rates in (("oct", oct_rates), ("jan", jan)):
            p = {f: parts(rates, f, kwh[f]) for f in FUELS}
            if name == "typical_dual_fuel" and label == "jan":
                # The stated per-fuel typical bills, so the example matches the headline.
                p = {f: {**p[f], "total": jan["typical"][f]} for f in FUELS}
            row[label] = {
                "electricity": p["electricity"]["total"],
                "gas": p["gas"]["total"],
                "total": p["electricity"]["total"] + p["gas"]["total"],
                "standing": p["electricity"]["standing"] + p["gas"]["standing"],
                "unit": p["electricity"]["unit"] + p["gas"]["unit"],
                "fuel_change_pct": {
                    f: (p[f]["total"] / pf - 1) if (pf := parts(oct_rates, f, kwh[f])["total"]) else None
                    for f in FUELS
                } if label == "jan" else None,
            }
        row["change"] = row["jan"]["total"] - row["oct"]["total"]
        row["change_pct"] = row["change"] / row["oct"]["total"]
        row["standing_share_jan"] = row["jan"]["standing"] / row["jan"]["total"]
        row["q1_change"] = sum(
            kwh[f] * (jan["unit"][f] - oct_rates["unit"][f]) / 100 * q1_share[f]
            + (q1_days * (jan["standing"][f] - oct_rates["standing"][f]) / 100 if kwh[f] else 0)
            for f in FUELS
        )
        examples[name] = row

    oct_typical = {f: bill(oct_rates["unit"][f], oct_rates["standing"][f], tdcv[f], days) for f in FUELS}
    fuel_change = {f: jan["typical"][f] - oct_typical[f] for f in FUELS}
    return {
        "oct_typical_bill": oct_typical,
        "oct_typical_total": sum(oct_typical.values()),
        "jan_typical_bill": jan["typical"],
        "jan_typical_total": sum(jan["typical"].values()),
        "factor": {f: jan["typical"][f] / oct_typical[f] for f in FUELS},
        "jan_unit_p_per_kwh": jan["unit"],
        "jan_standing_p_per_day": jan["standing"],
        "unit_change_pct": {f: jan["unit"][f] / oct_rates["unit"][f] - 1 for f in FUELS},
        "standing_change_pct": {f: jan["standing"][f] / oct_rates["standing"][f] - 1 for f in FUELS},
        "typical_fuel_change": fuel_change,
        "typical_fuel_change_pct": {f: fuel_change[f] / oct_typical[f] for f in FUELS},
        "gas_share_of_typical_change": fuel_change["gas"] / sum(fuel_change.values()),
        "q1_share": q1_share,
        "examples": examples,
    }


# ---------------------------------------------------------------- model


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def take_lock(job):
    while True:
        try:
            fd = os.open(LOCK, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o644)
        except FileExistsError:
            try:
                text = LOCK.read_text().strip()
                pid = int(text.split()[0])
                os.kill(pid, 0)
            except ProcessLookupError:
                print(f"removing stale lock ({text})", file=sys.stderr)
                LOCK.unlink(missing_ok=True)
                continue
            except (FileNotFoundError, IndexError, ValueError, PermissionError):
                pass
            print(f"waiting for {LOCK} ({LOCK.read_text().strip() if LOCK.exists() else ''})", file=sys.stderr)
            time.sleep(30)
            continue
        os.write(fd, f"{os.getpid()} uk-energy-price-cap {job}\n".encode())
        os.close(fd)
        return


def release_lock():
    try:
        if LOCK.read_text().split()[0] == str(os.getpid()):
            LOCK.unlink()
    except (FileNotFoundError, IndexError):
        pass


def model_figures(arrays, factor):
    w, gb, decile, net, pe_net, elec_q4, gas_q4 = (
        arrays[k] for k in ("w", "gb", "decile", "net", "pe_net", "elec_q4", "gas_q4")
    )
    before = elec_q4 + gas_q4
    after = elec_q4 * factor["electricity"] + gas_q4 * factor["gas"]
    change = after - before

    def wmean(x, m):
        return float(np.sum(x[m] * w[m]) / np.sum(w[m]))

    def wmedian(x, m):
        order = np.argsort(x[m])
        xs, ws = x[m][order], w[m][order]
        c = np.cumsum(ws)
        return float(xs[np.searchsorted(c, c[-1] / 2)])

    def share(x, m, income=net):
        return float(np.sum(x[m] * w[m]) / np.sum(income[m] * w[m]))

    def over_10pct(x):
        return float(w[gb & (x > 0) & ((net <= 0) | (x > 0.1 * net))].sum() / 1e6)

    dual = gb & (elec_q4 > 0) & (gas_q4 > 0)
    elec_only = gb & (elec_q4 > 0) & (gas_q4 == 0)
    out = {
        "gb": {
            "households_m": float(w[gb].sum() / 1e6),
            "households_dual_fuel_m": float(w[dual].sum() / 1e6),
            "households_electric_only_m": float(w[elec_only].sum() / 1e6),
            "households_no_energy_spend_m": float(w[gb & (before <= 0)].sum() / 1e6),
            "elec_total_bn_fy_model": float(np.sum(arrays["elec_fy"][gb] * w[gb]) / 1e9),
            "gas_total_bn_fy_model": float(np.sum(arrays["gas_fy"][gb] * w[gb]) / 1e9),
            "before_total_bn": float(np.sum(before[gb] * w[gb]) / 1e9),
            "after_total_bn": float(np.sum(after[gb] * w[gb]) / 1e9),
            "change_total_bn": float(np.sum(change[gb] * w[gb]) / 1e9),
            "mean_before": wmean(before, gb),
            "mean_after": wmean(after, gb),
            "mean_change": wmean(change, gb),
            "median_before": wmedian(before, gb),
            "dual_mean_before": wmean(before, dual),
            "dual_median_before": wmedian(before, dual),
            "dual_mean_change": wmean(change, dual),
            "elec_only_mean_before": wmean(before, elec_only),
            "elec_only_mean_change": wmean(change, elec_only),
            "share_of_income_before": share(before, gb),
            "share_of_income_after": share(after, gb),
            "spend_over_10pct_income_before_m": over_10pct(before),
            "spend_over_10pct_income_after_m": over_10pct(after),
            "share_of_household_net_income_before": share(before, gb, pe_net),
            "net_income_nonpositive_m": float(w[gb & (net <= 0)].sum() / 1e6),
        },
        "deciles": [],
    }
    hh_share = lambda x: np.where(net > 0, x / np.where(net > 0, net, 1), np.inf)
    for d in range(1, 11):
        m = gb & (decile == d)
        out["deciles"].append({
            "decile": d,
            "households_m": float(w[m].sum() / 1e6),
            "mean_net_income": wmean(net, m),
            "mean_elec_before": wmean(elec_q4, m),
            "mean_gas_before": wmean(gas_q4, m),
            "mean_before": wmean(before, m),
            "mean_after": wmean(after, m),
            "mean_change": wmean(change, m),
            "share_before": share(before, m),
            "share_after": share(after, m),
            "share_before_household_net_income": share(before, m, pe_net),
            "median_hh_share_before": wmedian(hh_share(before), m),
            "median_hh_share_after": wmedian(hh_share(after), m),
            "share_dual_fuel": float(w[m & dual].sum() / w[m].sum()),
        })
    return out


# The Budget's support, set against the change (all for Great Britain):
# - Household Energy Payment: the engine's household_energy_payment for
#   2026-27, a one-off £100 to households in council tax bands A to D in
#   England, paid from January 2027.
# - Electricity VAT: Ofgem's caps carry 0% VAT on electricity from 1 October
#   2026, so the zero rate is in both the October and the January bill and the
#   change between them already includes it. vat_on_change is what 5% VAT
#   would add to the change; vat_cut_jan what it would add to the January bill.
# The one-off payment is set against the change over January to March, not
# the annual-rate change; the post states the approximation.
VAT_FORGONE = 0.05


def hep_reach(arrays):
    """Who the Household Energy Payment reaches, by income decile."""
    w, gb, eng, hep, decile = (arrays[k] for k in ("w", "gb", "england", "hep", "decile"))
    got = hep > 0

    def share(m):
        return float(w[m & got].sum() / w[m].sum())

    out = {
        "recipients_m": float(w[gb & got].sum() / 1e6),
        "cost_bn": float(np.sum(hep[gb] * w[gb]) / 1e9),
        "share_gb": share(gb),
        "share_england": share(gb & eng),
        "england_households_m": float(w[gb & eng].sum() / 1e6),
        "deciles": [],
    }
    for d in range(1, 11):
        m = gb & (decile == d)
        out["deciles"].append({
            "decile": d,
            "share_gb": share(m),
            "share_england": share(m & eng),
            "mean_gb": float(np.sum(hep[m] * w[m]) / np.sum(w[m])),
            "missed_gb_m": float(w[m & ~got].sum() / 1e6),
            "missed_england_m": float(w[m & eng & ~got].sum() / 1e6),
        })
    return out


def support_figures(arrays, factor, q1_share):
    """The change in the bill, and the one-off payment set against the change
    over January to March. Both caps carry no VAT on electricity, so the change
    already includes the zero rate; vat_on_change is how much 5% VAT would add
    to the change, and vat_cut_jan / vat_cut_oct what it would add to the bill."""
    w, gb, eng, decile, hep, elec_q4, gas_q4 = (
        arrays[k] for k in ("w", "gb", "england", "decile", "hep", "elec_q4", "gas_q4")
    )
    d_elec = elec_q4 * (factor["electricity"] - 1)
    d_gas = gas_q4 * (factor["gas"] - 1)
    change = d_elec + d_gas
    # Approximation: each fuel's change scaled by its share of a year's use in
    # January to March (standing charges included in the scaled amount).
    change_q1 = d_elec * q1_share["electricity"] + d_gas * q1_share["gas"]

    def wm(x, m):
        return float(np.sum(x[m] * w[m]) / np.sum(w[m]))

    def row(m):
        return {
            "change": wm(change, m),
            "change_q1": wm(change_q1, m),
            "hep": wm(hep, m),
            "change_q1_net_hep": wm(change_q1 - hep, m),
            "vat_on_change": wm(d_elec * VAT_FORGONE, m),
            "vat_cut_jan": wm(elec_q4 * factor["electricity"] * VAT_FORGONE, m),
            "vat_cut_oct": wm(elec_q4 * VAT_FORGONE, m),
            "share_change_offset_by_hep": float(np.sum(hep[m] * w[m]) / np.sum(change[m] * w[m])),
            "share_change_q1_offset_by_hep": float(np.sum(hep[m] * w[m]) / np.sum(change_q1[m] * w[m])),
        }

    # The payment is England's; Wales and Scotland pay their own £100, which the
    # model does not cover, so the payment is set against the change in England.
    return {
        "gb": row(gb),
        "deciles": [{"decile": d, **row(gb & (decile == d))} for d in range(1, 11)],
        "england": row(gb & eng),
        "deciles_england": [{"decile": d, **row(gb & eng & (decile == d))} for d in range(1, 11)],
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--inputs", default=HERE / "inputs.json", type=Path)
    parser.add_argument("--out", type=Path, help="default: results/results-<policyengine version>.json")
    args = parser.parse_args()

    versions, bundle = installed_bundle()
    cfg = json.loads(args.inputs.read_text())
    out_path = args.out or HERE / "results" / f"results-{versions['policyengine']}.json"

    oct_cfg = cfg["october"]
    oct_rates = {"unit": oct_cfg["unit_p_per_kwh"], "standing": oct_cfg["standing_p_per_day"]}
    scenarios = {k: s for k, s in cfg["scenarios"].items() if scenario_is_filled(s)}
    rates = {k: resolve_rates(cfg, s) for k, s in scenarios.items()}
    print(f"scenarios: {', '.join(scenarios)} (unfilled: "
          f"{', '.join(k for k in cfg['scenarios'] if k not in scenarios) or 'none'})", file=sys.stderr)

    ds = dataset_path(bundle)
    if not ds.exists():
        raise SystemExit(f"{ds} not found: run download_data.py or set MICROCOSM_DATASET")
    if sha256(ds) != bundle["sha256"]:
        raise SystemExit(f"{ds} is not build {bundle['build']} (SHA-256 mismatch)")

    take_lock(f"run_cap {versions['policyengine']}")
    try:
        from policyengine_uk import Microsimulation

        sim = Microsimulation(dataset=str(ds))
        p = sim.tax_benefit_system.parameters.gov.economic_assumptions.energy_prices
        to_q4 = {
            f: float(getattr(p.quarterly, f)("2026-10-01"))
            / float(getattr(p.fiscal_year, f)(f"{YEAR}-01-01"))
            for f in FUELS
        }
        q1_share = {f: float(getattr(p.consumption_shares, f).q1(f"{YEAR}-01-01")) for f in FUELS}

        def calc(v):
            return np.asarray(sim.calculate(v, YEAR, map_to="household").values)

        elec_fy = calc("electricity_consumption").astype(float)
        gas_fy = calc("gas_consumption").astype(float)
        arrays = {
            "w": calc("household_weight").astype(float),
            "gb": calc("country").astype(str) != "NORTHERN_IRELAND",
            "decile": calc("household_income_decile").astype(int),
            "net": calc("hbai_household_net_income").astype(float),
            "pe_net": calc("household_net_income").astype(float),
            "elec_fy": elec_fy,
            "gas_fy": gas_fy,
            "elec_q4": elec_fy * to_q4["electricity"] / (1 + ENERGY_INPUT_VAT),
            "gas_q4": gas_fy * to_q4["gas"],
            "england": calc("country").astype(str) == "ENGLAND",
            "hep": calc("household_energy_payment").astype(float),
        }
    finally:
        release_lock()

    out = {
        "versions": versions,
        "dataset": {"build": bundle["build"], "sha256": bundle["sha256"]},
        "to_q4": to_q4,
        "october": {**oct_cfg, "rates": oct_rates},
        "history": cfg["history"]["quarters"],
        "peak_2022": {k: v for k, v in cfg.get("peak_2022", {}).items() if not k.startswith("_")},
        "decile_values_present": sorted(set(arrays["decile"][arrays["gb"]].tolist())),
        "hep_reach": hep_reach(arrays),
        "scenarios": {},
    }
    for key, s in scenarios.items():
        arith = rate_arithmetic(cfg, oct_rates, rates[key], q1_share)
        out["scenarios"][key] = {
            "label": s["label"],
            "kind": s["kind"],
            "source": s["source"],
            "announced_on": s.get("announced_on"),
            "typical_bill_announced": s["typical_bill_announced"],
            "inputs": {k: v for k, v in arith.items() if k != "examples"},
            "examples": arith["examples"],
            **model_figures(arrays, arith["factor"]),
            "support": support_figures(arrays, arith["factor"], q1_share),
        }
    out["unfilled_scenarios"] = [k for k in cfg["scenarios"] if k not in scenarios]

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(out, indent=2))
    for key, r in out["scenarios"].items():
        g = r["gb"]
        print(f"{key}: mean change £{g['mean_change']:.0f}, decile 1 £{r['deciles'][0]['mean_change']:.0f}, "
              f"decile 10 £{r['deciles'][9]['mean_change']:.0f}, decile 1 share "
              f"{r['deciles'][0]['share_before']:.1%} -> {r['deciles'][0]['share_after']:.1%}, "
              f"over 10% {g['spend_over_10pct_income_before_m']:.1f}m -> {g['spend_over_10pct_income_after_m']:.1f}m")
    print(out_path)


if __name__ == "__main__":
    main()

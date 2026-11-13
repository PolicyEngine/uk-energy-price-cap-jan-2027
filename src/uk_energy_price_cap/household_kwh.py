"""Household kilowatt-hours read straight from the Microcosm file.

Microcosm exports ``gas_kwh`` and ``electricity_kwh`` (calendar 2024) as
household columns. policyengine-uk does not expose them: its monthly kWh
inputs stay unfilled until policyengine-uk#2890 item 1. So this module
reads the two columns with h5py and joins them to the model's households
on ``household_id``.

``gas_kwh > 0`` identifies a gas household. On build
uk-frs-calibration-attempt-20261112T133744Z-6f918b81 it matches
``gas_consumption > 0`` on every row: 24.34m households weighted, 84.0%,
in line with DESNZ's 84% on gas (María Juaristi, 13 November 2026).

The file is a pandas table store: each entity is a group holding one
compound dataset, ``<entity>/table``, with one field per column. Only the
named fields are read.
"""

from pathlib import Path

KWH_COLUMNS = ("household_id", "gas_kwh", "electricity_kwh")
DAYS = 365


class KwhReadError(RuntimeError):
    """The kWh columns are missing or do not join to the model's rows."""


def read(path: Path | str, columns=KWH_COLUMNS) -> dict[str, list]:
    """The named household columns from the file, one list per column."""
    import h5py

    with h5py.File(Path(path).expanduser(), "r") as f:
        if "household/table" not in f:
            raise KwhReadError(f"{path}: no household/table dataset")
        table = f["household/table"]
        names = table.dtype.names or ()
        missing = [c for c in columns if c not in names]
        if missing:
            raise KwhReadError(f"{path}: no column(s) {', '.join(missing)}")
        rows = table.fields(list(columns))[:]
    return {c: rows[c].tolist() for c in columns}


def join(household_ids, path: Path | str) -> dict[str, list[float]]:
    """``gas_kwh`` and ``electricity_kwh`` in the order of ``household_ids``.

    Raises if any model household has no row in the file, or the file has
    a household twice: a gap is never filled with zero.
    """
    data = read(path)
    by_id: dict[int, int] = {}
    for i, hid in enumerate(data["household_id"]):
        hid = int(hid)
        if hid in by_id:
            raise KwhReadError(f"household_id {hid} appears twice in {path}")
        by_id[hid] = i
    out = {"gas_kwh": [], "electricity_kwh": []}
    unmatched = []
    for hid in household_ids:
        i = by_id.get(int(hid))
        if i is None:
            unmatched.append(int(hid))
            continue
        for column in out:
            value = float(data[column][i])
            if value < 0:
                raise KwhReadError(f"{column} < 0 for household_id {hid}")
            out[column].append(value)
    if unmatched:
        raise KwhReadError(
            f"{len(unmatched)} household(s) have no kWh row, e.g. "
            f"household_id {unmatched[0]}"
        )
    return out


def standing_charge_to_unit_rate(
    kwh: list[float],
    weights: list[float],
    in_cap: list[bool],
    standing_p_per_day: float,
    share: float = 1.0,
) -> tuple[list[float], float]:
    """Annual bill change per household when a standing charge moves.

    ``share`` of the standing charge (pence a day) comes off every bill
    in the cap that uses the fuel (``kwh > 0``) and is recovered through
    one higher unit rate, so the weighted total is unchanged. Households
    outside the cap (Northern Ireland) or without the fuel are unchanged.
    Returns (change in £ per household, unit-rate rise in p/kWh). Static:
    nobody changes how much energy they use.
    """
    removed = share * standing_p_per_day * DAYS / 100  # £ a year
    users = [k > 0 and c for k, c in zip(kwh, in_cap)]
    raised = sum(w for w, u in zip(weights, users) if u) * removed
    volume = sum(k * w for k, w, u in zip(kwh, weights, users) if u)
    if volume <= 0:
        return [0.0] * len(kwh), 0.0
    rise = raised / volume  # £ per kWh
    change = [k * rise - removed if u else 0.0 for k, u in zip(kwh, users)]
    return change, rise * 100

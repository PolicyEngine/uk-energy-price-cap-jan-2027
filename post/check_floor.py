"""Survey households behind each published cell (stdout only; never commit
the counts). Run before publishing figures on a new Microcosm build.

    uv run python check_floor.py
"""

import numpy as np
import pandas as pd

from bundles import dataset_path, installed_bundle
from run_cap import release_lock, take_lock

_, bundle = installed_bundle()
ds = str(dataset_path(bundle))
take_lock("check_floor")
try:
    from policyengine_uk import Microsimulation

    hh = pd.read_hdf(ds, "household")
    sim = Microsimulation(dataset=ds)
    c = lambda v: np.asarray(sim.calculate(v, 2026, map_to="household").values)
    hid = c("household_id").astype(int)
    src = hh.set_index("household_id").loc[hid, "source_household_id"].values
    gb = c("country").astype(str) != "NORTHERN_IRELAND"
    dec = c("household_income_decile").astype(int)
    e, g = c("electricity_consumption"), c("gas_consumption")
    net = c("hbai_household_net_income")
finally:
    release_lock()
cells = {"gb": gb, "dual": gb & (e > 0) & (g > 0), "elec_only": gb & (e > 0) & (g == 0),
         "nonpos_income": gb & (net <= 0)}
for d in range(1, 11):
    cells[f"decile{d}"] = gb & (dec == d)
for k, m in cells.items():
    print(k, "rows", int(m.sum()), "survey_hh", len(set(src[m])))

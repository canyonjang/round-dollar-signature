"""Checks that cell_ols reproduces (1) the published Table 1 and (2) transfer-level OLS/WLS
with dummies and day-clustered SEs on simulated micro data.  Run: python test_cellreg.py"""
import numpy as np, pandas as pd
import statsmodels.api as sm
from cellreg import cell_ols, add_dummies

# ---------- (1) published Table 1 from data/03 ----------
d = pd.read_csv("../data/03_size_stratified.csv")
d = d[d.size_bucket != "0_sub1"].copy()
d["n_whole"] = d.pct_whole_dollar / 100 * d.n          # 03 stores rounded % -> same as lpm.py
d["single"] = (d.tx_type == "1_single").astype(float)
x = ["single"] + add_dummies(d, "coin", ["USDT", "PYUSD"], "coin_") + \
    add_dummies(d, "size_bucket", ["2_10-100", "3_100-1k", "4_1k-10k", "5_10k-100k", "6_100k+"], "sz_")
r = cell_ols(d, "n", "n_whole", x, hc1=True)
pub = pd.read_csv("../figures/table1_lpm.csv").set_index("term")
assert abs(r["beta"][0] * 100 - pub.loc["single", "coef_pp"]) < 1e-9, r["beta"][0]
assert abs(r["se"][0] * 100 - pub.loc["single", "se_pp"]) < 1e-9, r["se"][0]
assert abs(r["const"] * 100 - pub.loc["const", "coef_pp"]) < 1e-9
print(f"[ok] published Table 1 reproduced: single = {r['beta'][0]*100:.4f} pp, HC1 se = {r['se'][0]*100:.6f}")

# ---------- (2) simulated micro data ----------
rng = np.random.default_rng(7)
n = 60000
mi = pd.DataFrame({
    "day": rng.integers(0, 40, n),
    "coin": rng.choice(["A", "B", "C"], n),
    "size": rng.choice(list("pqrs"), n),
    "single": rng.integers(0, 2, n).astype(float),
})
day_eff = rng.normal(0, 0.05, 40)
p = 0.1 + 0.2 * mi.single + 0.05 * (mi.coin == "B") + 0.03 * (mi["size"] == "r") + day_eff[mi.day]
mi["y"] = (rng.random(n) < p.clip(0.01, 0.99)).astype(float)
mi["amt"] = rng.lognormal(3, 1.5, n)
mi["ya"] = mi.y * mi.amt

keys = ["day", "coin", "size", "single"]
cells = mi.groupby(keys).agg(n=("y", "size"), n_whole=("y", "sum"),
                             A=("amt", "sum"), A_whole=("ya", "sum")).reset_index()
xs = ["single"] + add_dummies(cells, "coin", ["B", "C"], "c_") + add_dummies(cells, "size", list("qrs"), "s_")
add_dummies(mi, "coin", ["B", "C"], "c_"); add_dummies(mi, "size", list("qrs"), "s_")

# 2a: count-weighted, constant, day-clustered
r = cell_ols(cells, "n", "n_whole", xs, cluster="day")
m = sm.OLS(mi.y, sm.add_constant(mi[xs])).fit(cov_type="cluster", cov_kwds={"groups": mi.day})
assert np.allclose(r["beta"], m.params[xs].values, atol=1e-10)
assert np.allclose(r["se"], m.bse[xs].values, rtol=1e-6), (r["se"], m.bse[xs].values)
print("[ok] count-weighted LPM, day-clustered SEs match micro OLS")

# 2b: HC1
r = cell_ols(cells, "n", "n_whole", xs, hc1=True)
m = sm.OLS(mi.y, sm.add_constant(mi[xs])).fit(cov_type="HC1")
assert np.allclose(r["se"], m.bse[xs].values, rtol=1e-6)
print("[ok] HC1 SEs match micro OLS")

# 2c: absorbed coin x size x day FE, day-clustered
cells["g"] = cells.coin + cells["size"] + cells.day.astype(str)
mi["g"] = mi.coin + mi["size"] + mi.day.astype(str)
r = cell_ols(cells, "n", "n_whole", ["single"], absorb="g", cluster="day")
D = pd.get_dummies(mi.g, drop_first=True, dtype=float)
m = sm.OLS(mi.y, sm.add_constant(pd.concat([mi[["single"]], D], axis=1))).fit(
    cov_type="cluster", cov_kwds={"groups": mi.day})
assert abs(r["beta"][0] - m.params["single"]) < 1e-10
# statsmodels counts every dummy in K; we follow Stata/reghdfe (FE nested in clusters not
# counted). Compare the sandwich before the small-sample factor.
G = 40
Kd = D.shape[1] + 2
ours_raw = r["se"][0] / np.sqrt(G / (G - 1) * (n - 1) / (n - 2))
sm_raw = m.bse["single"] / np.sqrt(G / (G - 1) * (n - 1) / (n - Kd))
assert abs(ours_raw - sm_raw) < 1e-10, (ours_raw, sm_raw)
print("[ok] absorbed issuer x size x day FE matches micro OLS with dummies")

# 2d: value-weighted (WLS with weights = USD amount), day-clustered
r = cell_ols(cells, "A", "A_whole", xs, cluster="day", nobs=n)
m = sm.WLS(mi.y, sm.add_constant(mi[xs]), weights=mi.amt).fit(cov_type="cluster", cov_kwds={"groups": mi.day})
assert np.allclose(r["beta"], m.params[xs].values, atol=1e-10)
assert np.allclose(r["se"], m.bse[xs].values, rtol=1e-6), (r["se"], m.bse[xs].values)
print("[ok] value-weighted WLS, day-clustered SEs match micro WLS")
print("all tests passed")

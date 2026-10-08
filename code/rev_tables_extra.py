"""Additional revision exhibits requested in the pre-submission review.

  T7  Value-weighted single-transfer coefficient: sensitivity to the largest transfers and by issuer
      (R02c day cells, excl. mint/burn; day FE; day-clustered SEs).
  T8  Transfers into payment-processor addresses by processor, with leave-one-out shares (R05).
  T9  Reconciliation of mint/burn-excluded counts in Tables S5 (query 07) and S7 (R02b).
Run: python rev_tables_extra.py
"""
import os
import pandas as pd
from cellreg import cell_ols, add_dummies

D, OUT = "../data/", "../figures/rev/"
os.makedirs(OUT, exist_ok=True)
SZ = ["2_10-100", "3_100-1k", "4_1k-10k", "5_10k-100k", "6_100k+"]

# ---------------- T7
c = pd.read_csv(D + "R02c_cells_day_endpoint.csv")
for k in ("sum_amt", "sum_amt_whole"):
    c[k] = pd.to_numeric(c[k])
v = c.groupby(["dt", "coin", "tx_type", "size_bucket"], as_index=False)[["n", "n_whole", "sum_amt", "sum_amt_whole"]].sum()
v = v[v.size_bucket != "0_sub1"].copy()
v["single"] = (v.tx_type == "1_single").astype(float)


def est(x, label):
    x = x.copy()
    coins = [k for k in ["USDT", "PYUSD"] if x.coin.nunique() > 1 and k in set(x.coin)]
    xs = add_dummies(x, "coin", coins, "c_") + add_dummies(x, "size_bucket", [s for s in SZ if s in set(x.size_bucket)], "s_")
    rv = cell_ols(x, "sum_amt", "sum_amt_whole", ["single"] + xs, absorb="dt", cluster="dt", nobs=x.n.sum())
    rc = cell_ols(x, "n", "n_whole", ["single"] + xs, absorb="dt", cluster="dt")
    return {"sample": label, "value_weighted_pp": round(rv["beta"][0] * 100, 2), "vw_se": round(rv["se"][0] * 100, 3),
            "count_weighted_pp": round(rc["beta"][0] * 100, 2), "cw_se": round(rc["se"][0] * 100, 3),
            "transfers_m": round(x.n.sum() / 1e6, 1), "usd_volume_bn": round(x.sum_amt.sum() / 1e9, 1)}


rows = [est(v, "All transfers >= $1"),
        est(v[v.size_bucket != "6_100k+"], "Excluding transfers > $100k"),
        est(v[~v.size_bucket.isin(["5_10k-100k", "6_100k+"])], "Excluding transfers > $10k")]
rows += [est(v[v.coin == k], f"{k} only") for k in ["USDT", "USDC", "PYUSD"]]
t7 = pd.DataFrame(rows)
t7.to_csv(OUT + "T7_value_weighted_sensitivity.csv", index=False)
print("## T7 value-weighted sensitivity (day FE, day-clustered, excl. mint/burn)\n", t7.to_string(index=False), "\n")

# ---------------- T8
p = pd.read_csv(D + "R05_psp_by_address.csv")
p = p[(p.size_bucket != "0_sub1") & (p.tx_type == "1_single")].copy()
p["processor"] = p.name_tag.str.extract(r"^(BitPay|AlphaPo|Upay|Zovix|Coinbase|B2BinPay|Paykassa|Transak|WooCommerce)")[0].fillna(p.name_tag)
g = p.groupby("processor")[["n", "n_whole", "n_cent"]].sum()
rows = []
for name, r in g.sort_values("n", ascending=False).iterrows():
    rest = g.drop(index=name).sum()
    rows.append({"processor": name, "transfers": int(r.n), "share_pct": round(r.n / g.n.sum() * 100, 2),
                 "whole_pct": round(r.n_whole / r.n * 100, 2), "cent_pct": round(r.n_cent / r.n * 100, 2),
                 "excluding_this_whole_pct": round(rest.n_whole / rest.n * 100, 2),
                 "excluding_this_cent_pct": round(rest.n_cent / rest.n * 100, 2)})
tot = g.sum()
rows.append({"processor": "All processors", "transfers": int(tot.n), "share_pct": 100.0,
             "whole_pct": round(tot.n_whole / tot.n * 100, 2), "cent_pct": round(tot.n_cent / tot.n * 100, 2)})
t8 = pd.DataFrame(rows)
bp = p[p.processor == "BitPay"].groupby("size_bucket")[["n", "n_whole", "n_cent"]].sum()
bp["whole_pct"] = (bp.n_whole / bp.n * 100).round(2); bp["cent_pct"] = (bp.n_cent / bp.n * 100).round(2)
t8.to_csv(OUT + "T8_psp_by_processor.csv", index=False)
bp.reset_index().to_csv(OUT + "T8b_bitpay_by_size.csv", index=False)
print("## T8 payment-processor inflows by processor (single, >= $1)\n", t8.to_string(index=False))
print(bp, "\n")

# ---------------- T9
s5 = pd.read_csv(D + "07_exclude_zero_address.csv").set_index(["coin", "tx_type"]).n_transfers
b = pd.read_csv(D + "R02b_cells_attr.csv")
s7 = b[b.cpty_cat != "mint_burn"].groupby(["coin", "tx_type"]).n.sum()
t9 = pd.DataFrame({"S5_query07": s5, "S7_R02b": s7})
t9["difference"] = t9.S5_query07 - t9.S7_R02b
t9.reset_index().to_csv(OUT + "T9_s5_s7_reconciliation.csv", index=False)
print("## T9 S5 vs S7 counts (same total; transaction structure defined before vs after dropping mint/burn legs)\n", t9)

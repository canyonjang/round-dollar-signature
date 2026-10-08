"""Revision exhibits (responses to referees), built from the R02a/R02b/R03/R04 query outputs.

Run:  python rev_tables.py          (reads ../data/R0*.csv; skips any file that is missing)
Writes CSV tables to ../figures/rev/ and a plain-text digest ../figures/rev/revision_results.md

  T1  Revised Table 1: explicit LPM, conventional layout; baseline (cell-level, HC1),
      + day FE (day-clustered), issuer x size x day FE (day-clustered), value-weighted.
  T2  Robustness of the single-vs-multi contrast to sample restrictions (labels, EOA/contract,
      high-volume addresses, mint/burn, direct wallet calls).
  T3  Counterparty composition and label-based validation (payment processors, exchanges,
      issuers, DeFi) with whole-dollar, whole-cent and $X.99 shares.
  T4  Count- vs value-weighted whole-dollar shares.
  T5  Cross-chain replication (Tron USDT; optional Polygon USDC/USDT) vs Ethereum, same month.
"""
import os
import numpy as np
import pandas as pd
from cellreg import cell_ols, add_dummies

D = "../data/"
OUT = "../figures/rev/"
os.makedirs(OUT, exist_ok=True)
SIZES = ["1_1-10", "2_10-100", "3_100-1k", "4_1k-10k", "5_10k-100k", "6_100k+"]
SIZE_DUMMIES = SIZES[1:]                     # omitted: $1-10
md = []                                       # digest lines


def say(s=""):
    print(s)
    md.append(s)


def pp(x):
    return f"{x * 100:.2f}"


def load(name):
    p = D + name
    if not os.path.exists(p):
        say(f"[skip] {name} not found")
        return None
    df = pd.read_csv(p)
    for c in ("sum_amt", "sum_amt_whole"):
        if c in df:
            df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0.0)
    for c in ("direct_call", "from_contract", "to_contract", "hv"):
        if c in df and df[c].dtype != bool:
            df[c] = df[c].astype(str).str.lower().isin(["true", "1"])
    return df


def prep(df):
    d = df[df.size_bucket != "0_sub1"].copy()    # whole dollars impossible below $1
    d["single"] = (d.tx_type == "1_single").astype(float)
    return d


def shares(df, by):
    g = df.groupby(by)[["n", "n_whole"]].sum()
    return (g.n_whole / g.n)


# ============================== T1 ==============================
a = load("R02a_cells_day.csv")
if a is not None:
    d = prep(a)
    d["day"] = d.dt.astype(str)
    xc = add_dummies(d, "coin", ["USDT", "PYUSD"], "coin_")      # omitted: USDC
    xs = add_dummies(d, "size_bucket", SIZE_DUMMIES, "sz_")
    col = {}

    # (1) published spec: 42 cells (coin x type x size), HC1
    c1 = d.groupby(["coin", "tx_type", "size_bucket"], as_index=False)[["n", "n_whole"]].sum()
    c1["single"] = (c1.tx_type == "1_single").astype(float)
    add_dummies(c1, "coin", ["USDT", "PYUSD"], "coin_"); add_dummies(c1, "size_bucket", SIZE_DUMMIES, "sz_")
    col["(1) Baseline"] = cell_ols(c1, "n", "n_whole", ["single"] + xc + xs, hc1=True)

    # (2) + day FE, day-clustered
    col["(2) + day FE"] = cell_ols(d, "n", "n_whole", ["single"] + xc + xs, absorb="day", cluster="day")

    # (3) issuer x size x day FE: single identified only within the same coin, size bucket and day
    d["g_csd"] = d.coin + "|" + d.size_bucket + "|" + d.day
    col["(3) issuer x size x day FE"] = cell_ols(d, "n", "n_whole", ["single"], absorb="g_csd", cluster="day")

    # (4) value-weighted (each transfer weighted by its USD amount), day FE, day-clustered
    col["(4) value-weighted"] = cell_ols(d, "sum_amt", "sum_amt_whole", ["single"] + xc + xs,
                                         absorb="day", cluster="day", nobs=d.n.sum())

    terms = ["single"] + xc + xs
    rows = []
    for t in terms:
        r1, r2 = {"term": t}, {"term": ""}
        for k, r in col.items():
            if t in r["xcols"]:
                j = r["xcols"].index(t)
                r1[k] = f"{r['beta'][j] * 100:.2f}"
                r2[k] = f"({r['se'][j] * 100:.3f})"
            else:
                r1[k] = r2[k] = ""
        rows += [r1, r2]
    base = c1[(c1.coin == "USDC") & (c1.tx_type == "2_multi") & (c1.size_bucket == "1_1-10")]
    foot = {
        "Baseline mean, multi/USDC/$1-10 (%)": [pp(base.n_whole.sum() / base.n.sum())] + [""] * 3,
        "Sample mean whole-dollar share (%)": [pp(r["mean_y"]) for r in col.values()],
        "Transfers (N)": [f"{int(r['nobs']):,}" for r in col.values()],
        "Cells": [f"{r['ncells']:,}" for r in col.values()],
        "Issuer FE / size FE": ["Yes", "Yes", "absorbed", "Yes"],
        "Day FE": ["No", "Yes", "absorbed", "Yes"],
        "Weights": ["transfers", "transfers", "transfers", "USD value"],
        "Standard errors": ["HC1"] + [f"clustered by day ({r['nclusters']})" for r in list(col.values())[1:]],
    }
    for k, v in foot.items():
        rows.append({"term": k, **dict(zip(col.keys(), v))})
    t1 = pd.DataFrame(rows)
    t1.to_csv(OUT + "T1_revised_table1.csv", index=False)
    say("## T1 Revised Table 1 (coefficients in pp, SE in parentheses)")
    say(t1.to_string(index=False))
    say()

    # ============================== T4 ==============================
    g = a.groupby(["coin", "tx_type"])[["n", "n_whole", "sum_amt", "sum_amt_whole"]].sum()
    t4 = pd.DataFrame({
        "n_transfers": g.n,
        "count_share_whole_pct": (g.n_whole / g.n * 100).round(2),
        "usd_volume_bn": (g.sum_amt / 1e9).round(2),
        "value_share_whole_pct": (g.sum_amt_whole / g.sum_amt * 100).round(2),
    }).reset_index()
    gb = a.groupby(["tx_type", "size_bucket"])[["n", "n_whole", "sum_amt", "sum_amt_whole"]].sum()
    t4b = pd.DataFrame({"count_share_whole_pct": (gb.n_whole / gb.n * 100).round(2),
                        "value_share_whole_pct": (gb.sum_amt_whole / gb.sum_amt * 100).round(2),
                        "usd_volume_share_pct": (gb.sum_amt / a.sum_amt.sum() * 100).round(2)}).reset_index()
    tot = a[["sum_amt", "sum_amt_whole"]].sum()
    single_whole_usd = a.loc[a.tx_type == "1_single", "sum_amt_whole"].sum()
    t4.to_csv(OUT + "T4_value_weighted.csv", index=False)
    t4b.to_csv(OUT + "T4b_value_weighted_by_size.csv", index=False)
    say("## T4 Count- vs value-weighted whole-dollar shares")
    say(t4.to_string(index=False))
    say(f"Whole-dollar transfers = {tot.sum_amt_whole / tot.sum_amt * 100:.2f}% of all USD volume; "
        f"whole-dollar SINGLE transfers = {single_whole_usd / tot.sum_amt * 100:.2f}% of all USD volume.")
    say(t4b.to_string(index=False))
    say()

# ============================== T2 / T3 ==============================
b = load("R02b_cells_attr.csv")
if b is not None:
    d = prep(b)
    d["g_csm"] = d.coin + "|" + d.size_bucket + "|" + d.month.astype(str)

    def contrast(sub, label, treat=None):
        """single-vs-multi LPM with issuer x size x month FE; HC1 SE."""
        s = sub.copy()
        if treat is not None:
            s = s[treat(s)]
        if s.single.nunique() < 2:
            return {"sample": label, "coef_pp": np.nan}
        r = cell_ols(s, "n", "n_whole", ["single"], absorb="g_csm", hc1=True)
        sh = shares(s, "tx_type")
        return {"sample": label, "coef_pp": round(r["beta"][0] * 100, 2), "se_pp": round(r["se"][0] * 100, 4),
                "whole_single_pct": round(sh.get("1_single", np.nan) * 100, 2),
                "whole_multi_pct": round(sh.get("2_multi", np.nan) * 100, 2),
                "n_transfers": int(s.n.sum()), "share_of_full_sample_pct": round(s.n.sum() / d.n.sum() * 100, 1)}

    lab = d.cpty_cat.isin(["psp", "issuer", "cex", "defi", "other"])
    eoa = ~d.from_contract & ~d.to_contract
    rows = [
        contrast(d, "Full sample (>= $1)"),
        contrast(d[d.cpty_cat != "mint_burn"], "Excl. mint/burn"),
        contrast(d[~d.cpty_cat.isin(["cex", "issuer"])], "Excl. exchange & issuer counterparties"),
        contrast(d[~lab & (d.cpty_cat != "mint_burn")], "Unlabeled counterparties only"),
        contrast(d[~d.hv], "Excl. 1,000 most active senders/recipients"),
        contrast(d[eoa], "EOA-to-EOA transfers only"),
        contrast(d, "Single = direct wallet call only (vs multi)",
                 treat=lambda s: (s.tx_type == "2_multi") | s.direct_call),
        contrast(d, "Single = contract-mediated only (vs multi)",
                 treat=lambda s: (s.tx_type == "2_multi") | ~s.direct_call),
        contrast(d[~lab & ~d.hv & eoa & (d.cpty_cat != "mint_burn")], "Strictest: unlabeled, not high-volume, EOA-to-EOA"),
    ]
    t2 = pd.DataFrame(rows)
    t2.to_csv(OUT + "T2_robustness.csv", index=False)
    say("## T2 Robustness: single-transfer coefficient (pp), issuer x size x month FE, HC1")
    say(t2.to_string(index=False))
    say()

    # T3: composition of single transfers by counterparty
    def comp(sub):
        g = sub.groupby(["cpty_cat", "cpty_dir"])[["n", "n_whole", "n_cent", "n_x99", "sum_amt", "sum_amt_whole"]].sum()
        out = pd.DataFrame({
            "n_transfers": g.n,
            "share_of_transfers_pct": (g.n / g.n.sum() * 100).round(2),
            "share_of_whole_dollar_transfers_pct": (g.n_whole / g.n_whole.sum() * 100).round(2),
            "whole_dollar_pct": (g.n_whole / g.n * 100).round(2),
            "whole_cent_pct": (g.n_cent / g.n * 100).round(2),
            "x99_pct": (g.n_x99 / g.n * 100).round(3),
            "value_weighted_whole_pct": (g.sum_amt_whole / g.sum_amt * 100).round(2),
        }).reset_index()
        return out.sort_values("n_transfers", ascending=False)

    t3s = comp(d[d.tx_type == "1_single"]); t3s.insert(0, "tx_type", "single")
    t3m = comp(d[d.tx_type == "2_multi"]); t3m.insert(0, "tx_type", "multi")
    t3 = pd.concat([t3s, t3m])
    t3.to_csv(OUT + "T3_counterparty_composition.csv", index=False)
    say("## T3 Counterparty composition (transfers >= $1)")
    say(t3.to_string(index=False))
    say()

    # direct vs contract-mediated singles, EOA/contract split (Referee 2)
    s1 = d[d.tx_type == "1_single"]
    t3c = s1.groupby(["direct_call", "from_contract", "to_contract"])[["n", "n_whole", "n_cent"]].sum()
    t3c["share_pct"] = (t3c.n / t3c.n.sum() * 100).round(2)
    t3c["whole_dollar_pct"] = (t3c.n_whole / t3c.n * 100).round(2)
    t3c = t3c.reset_index()
    t3c.to_csv(OUT + "T3c_single_by_call_type.csv", index=False)
    say("## T3c Single transfers by call type and account type")
    say(t3c.to_string(index=False))
    say()

# ============================== T5 ==============================
ext = [x for x in (load("R03_tron_cells.csv"), load("R04_polygon_cells.csv")) if x is not None]
if ext:
    rows = []
    if a is not None:   # Ethereum, same month (June 2025) from the day cells
        e = a[pd.to_datetime(a.dt).dt.month == 6].copy()
        e["chain"] = "ETHEREUM"
        ext = [e] + ext
    for x in ext:
        for (ch, cn), s in x.groupby(["chain", "coin"]):
            sd = prep(s)
            sd = sd.groupby(["tx_type", "size_bucket"], as_index=False)[["n", "n_whole"]].sum()
            sd["single"] = (sd.tx_type == "1_single").astype(float)
            r = cell_ols(sd, "n", "n_whole", ["single"], absorb="size_bucket", hc1=True)
            sh = shares(s, "tx_type")
            row = {"chain": ch, "coin": cn, "n_transfers": int(s.n.sum()),
                   "single_share_of_transfers_pct": round(s[s.tx_type == "1_single"].n.sum() / s.n.sum() * 100, 1),
                   "whole_single_pct": round(sh.get("1_single", np.nan) * 100, 2),
                   "whole_multi_pct": round(sh.get("2_multi", np.nan) * 100, 2),
                   "lpm_single_pp_sizeFE": round(r["beta"][0] * 100, 2), "se_pp": round(r["se"][0] * 100, 4)}
            if "n_half" in s:
                ss = s[s.tx_type == "1_single"]
                for c in ("n_whole", "n_half", "n_37", "n_123456"):
                    row[f"single_{c}_pct"] = round(ss[c].sum() / ss.n.sum() * 100, 4)
            if "sum_amt" in s:
                row["value_share_whole_pct"] = round(s.sum_amt_whole.sum() / s.sum_amt.sum() * 100, 2)
            rows.append(row)
    t5 = pd.DataFrame(rows)
    t5.to_csv(OUT + "T5_cross_chain.csv", index=False)
    say("## T5 Cross-chain replication, June 2025")
    say(t5.to_string(index=False))
    say()

with open(OUT + "revision_results.md", "w") as f:
    f.write("\n".join(md))
print("\nwritten:", sorted(os.listdir(OUT)))

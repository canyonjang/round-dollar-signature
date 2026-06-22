# Linear probability model: Pr(whole-dollar) ~ single + issuer FE + size FE
# Exact micro-OLS recovered from cell aggregates; HC1-robust SEs. Reads ../data/03_size_stratified.csv
import pandas as pd, numpy as np
d = pd.read_csv("../data/03_size_stratified.csv")
d = d[d.size_bucket != "0_sub1"].copy()              # whole-$ impossible below $1
d["p"] = d.pct_whole_dollar/100.0; d["n"] = d.n.astype(float)
cols = ["const","single","coin_USDT","coin_PYUSD","sz_10_100","sz_100_1k","sz_1k_10k","sz_10k_100k","sz_100k+"]
def row(r):
    return [1.0, 1.0 if r.tx_type=="1_single" else 0.0,
            1.0 if r.coin=="USDT" else 0.0, 1.0 if r.coin=="PYUSD" else 0.0,
            1.0 if r.size_bucket=="2_10-100" else 0.0, 1.0 if r.size_bucket=="3_100-1k" else 0.0,
            1.0 if r.size_bucket=="4_1k-10k" else 0.0, 1.0 if r.size_bucket=="5_10k-100k" else 0.0,
            1.0 if r.size_bucket=="6_100k+" else 0.0]
X = np.array([row(r) for r in d.itertuples()]); n=d.n.values; p=d.p.values
N=n.sum(); k=X.shape[1]
XtWX = X.T@(X*n[:,None]); beta=np.linalg.solve(XtWX, X.T@(n*p)); fit=X@beta
meat_w = n*p*(1-fit)**2 + n*(1-p)*(fit**2)
B=np.linalg.inv(XtWX); V=B@(X.T@(X*meat_w[:,None]))@B*(N/(N-k)); se=np.sqrt(np.diag(V))
out = pd.DataFrame({"term":cols,"coef_pp":beta*100,"se_pp":se*100,"t":beta/se})
out.to_csv("../figures/table1_lpm.csv", index=False)
print(f"N (>= $1) = {N:,.0f}   cells = {len(d)}   k = {k}")
print(out.to_string(index=False))

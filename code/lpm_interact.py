import pandas as pd, numpy as np, itertools
d = pd.read_csv("../data/03_size_stratified.csv")
d = d[d.size_bucket!="0_sub1"].copy()
d["p"]=d.pct_whole_dollar/100.0; d["n"]=d.n.astype(float)
coins=["USDC","USDT","PYUSD"]; sizes=["1_1-10","2_10-100","3_100-1k","4_1k-10k","5_10k-100k","6_100k+"]
# full issuer x size interaction dummies (baseline = USDC x 1_1-10), plus single dummy + const
groups=[(c,s) for c in coins for s in sizes]; base=("USDC","1_1-10")
groups=[g for g in groups if g!=base]
def row(r):
    v=[1.0, 1.0 if r.tx_type=="1_single" else 0.0]
    for g in groups: v.append(1.0 if (r.coin,r.size_bucket)==g else 0.0)
    return v
X=np.array([row(r) for r in d.itertuples()]); n=d.n.values; p=d.p.values; N=n.sum(); k=X.shape[1]
XtWX=X.T@(X*n[:,None]); beta=np.linalg.solve(XtWX,X.T@(n*p)); fit=X@beta
meat=n*p*(1-fit)**2+n*(1-p)*fit**2; B=np.linalg.inv(XtWX)
V=B@(X.T@(X*meat[:,None]))@B*(N/(N-k)); se=np.sqrt(np.diag(V))
print(f"issuer x size interaction FE  (N={N:,.0f}, cells={len(d)}, params={k})")
print(f"  single coef = {beta[1]*100:.3f} pp   HC1 s.e. = {se[1]*100:.4f} pp   t = {beta[1]/se[1]:.0f}")

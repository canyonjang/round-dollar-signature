import pandas as pd, numpy as np
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm

U = "../data/"
OUT = "../figures/"
import os; os.makedirs(OUT, exist_ok=True)

# --- style: clean journal look ---
plt.rcParams.update({
    "font.family":"DejaVu Sans","font.size":10,"axes.spines.top":False,
    "axes.spines.right":False,"axes.grid":True,"grid.alpha":0.25,
    "grid.linewidth":0.6,"axes.linewidth":0.8,"figure.dpi":150,
    "savefig.dpi":300,"savefig.bbox":"tight","legend.frameon":False,
})
C = {"USDT":"#2ca02c","USDC":"#1f77b4","PYUSD":"#d62728"}
ORDER = ["USDT","USDC","PYUSD"]

agg   = pd.read_csv(U+"01_aggregate.csv")
sm    = pd.read_csv(U+"02_single_multi.csv")
size  = pd.read_csv(U+"03_size_stratified.csv")
plac  = pd.read_csv(U+"04_placebo.csv")

# ============ FIG 1: aggregate round-number share by coin & denomination ============
denoms = ["pct_whole_dollar","pct_mult_10","pct_mult_100","pct_mult_1000"]
dlab   = ["multiple of $1","multiple of $10","multiple of $100","multiple of $1,000"]
fig,ax = plt.subplots(figsize=(7.0,3.6))
x = np.arange(len(denoms)); w=0.26
for i,c in enumerate(ORDER):
    r = agg.loc[agg.coin==c, denoms].values.flatten()
    ax.bar(x+(i-1)*w, r, w, label=c, color=C[c], edgecolor="white", linewidth=0.5)
ax.axhline(0.0001, ls=":", lw=1, color="0.4")
ax.text(3.3,0.00012,"no-preference null\n(1/10⁶ = 0.0001%)",fontsize=7,color="0.4",va="bottom",ha="right")
ax.set_yscale("log")
ax.set_xticks(x); ax.set_xticklabels(dlab, fontsize=9)
ax.set_ylabel("Share of transfers (%, log scale)")
ax.set_title("Round-number clustering in stablecoin transfer amounts (2025)", fontsize=10.5, loc="left")
ax.legend(ncol=3, loc="upper right", fontsize=9)
fig.savefig(OUT+"fig1_roundshare_by_coin.pdf"); fig.savefig(OUT+"fig1_roundshare_by_coin.png"); plt.close(fig)

# ============ FIG 2 (centerpiece): size-stratified single vs multi ============
buckets = ["1_1-10","2_10-100","3_100-1k","4_1k-10k","5_10k-100k","6_100k+"]
blab    = ["$1–10","$10–100","$100–1k","$1k–10k","$10k–100k","$100k+"]
fig,axes = plt.subplots(1,3,figsize=(9.2,3.3),sharey=True)
for ax,c in zip(axes,ORDER):
    d = size[(size.coin==c)&(size.size_bucket.isin(buckets))]
    s = d[d.tx_type=="1_single"].set_index("size_bucket").reindex(buckets)["pct_whole_dollar"]
    m = d[d.tx_type=="2_multi"].set_index("size_bucket").reindex(buckets)["pct_whole_dollar"]
    xx=np.arange(len(buckets))
    ax.plot(xx,s.values,"-o",color=C[c],lw=2,ms=5,label="single transfer (payment-like)")
    ax.plot(xx,m.values,"--s",color=C[c],lw=1.6,ms=4,mfc="white",label="multi transfer (machine-like)")
    ax.set_title(c,fontsize=10.5,color=C[c],fontweight="bold")
    ax.set_xticks(xx); ax.set_xticklabels(blab,rotation=45,ha="right",fontsize=8)
    ax.set_ylim(0,60)
axes[0].set_ylabel("Whole-dollar share (%)")
axes[1].legend(loc="upper center",bbox_to_anchor=(0.5,-0.32),ncol=2,fontsize=8.5)
fig.suptitle("Single-transfer whole-dollar shares exceed multi-transfer shares in every size bucket",
             fontsize=10.5,x=0.02,ha="left")
fig.savefig(OUT+"fig2_size_stratified.pdf"); fig.savefig(OUT+"fig2_size_stratified.png"); plt.close(fig)

# ============ FIG 3: placebo digit test (single transfers) ============
cats = ["pct_resid_000000_whole","pct_resid_500000_half","pct_resid_370000_placebo","pct_resid_123456_placebo"]
clab = ["$X.00\n(round)","$X.50\n(semi-round)","$X.37\n(placebo)","$X.123456\n(placebo)"]
ps = plac[plac.tx_type=="1_single"]
fig,ax = plt.subplots(figsize=(7.0,3.6))
x=np.arange(len(cats)); w=0.26
floor=0.00008
for i,c in enumerate(ORDER):
    r = ps.loc[ps.coin==c, cats].values.flatten().astype(float)
    r = np.where(r<=0, floor, r)
    ax.bar(x+(i-1)*w, r, w, label=c, color=C[c], edgecolor="white", linewidth=0.5)
ax.axhline(0.0001, ls=":", lw=1, color="0.4")
ax.text(3.4,0.00011,"no-preference null (1/10⁶)",fontsize=7,color="0.4",va="bottom",ha="right")
ax.set_yscale("log")
ax.set_xticks(x); ax.set_xticklabels(clab,fontsize=8.5)
ax.set_ylabel("Share of single-transfer payments (%, log scale)")
ax.set_title("Placebo digit test: mass concentrates at round and semi-round targets, not arbitrary residues",fontsize=10.5,loc="left")
ax.legend(ncol=3,loc="upper right",fontsize=9)
fig.savefig(OUT+"fig3_placebo.pdf"); fig.savefig(OUT+"fig3_placebo.png"); plt.close(fig)

print("done")
print(os.listdir(OUT))

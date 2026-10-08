"""Exact transfer-level linear probability models estimated from cell aggregates.

Every regressor in the paper is constant within a cell (issuer, transaction type, size bucket,
day, ...), so the transfer-level OLS / WLS estimates, residual sums and cluster scores can be
recovered exactly from four cell totals. Nothing here is an approximation of the micro
regression: coefficients and standard errors equal those from running OLS on the hundreds of
millions of underlying transfers.

Cell inputs
  W  : total weight in the cell   (n transfers for count-weighted, USD value for value-weighted)
  Y  : weighted sum of the outcome (n_whole, or USD value of whole-dollar transfers)

Model:  y_i = x_c' b + a_g + e_i , with optional absorbed fixed effects a_g (group g contains
cells). Standard errors: cluster-robust (any cell-level cluster variable, e.g. day) or HC1
(count weights and binary y only, which needs only n and n_whole per cell).
Small-sample factors follow Stata: cluster G/(G-1)*(N-1)/(N-K); HC1 N/(N-K).
"""
import numpy as np
import pandas as pd


def cell_ols(df, W, Y, xcols, absorb=None, cluster=None, hc1=False, nobs=None):
    d = df[df[W] > 0].copy()
    w = d[W].to_numpy(float)
    ysum = d[Y].to_numpy(float)
    X = d[xcols].to_numpy(float)
    k = X.shape[1]

    if absorb is None:
        g = np.zeros(len(d), dtype=int)
    else:
        g = pd.factorize(pd.MultiIndex.from_frame(d[absorb]) if isinstance(absorb, list)
                         else d[absorb])[0]
    G_abs = g.max() + 1

    # weighted group means of x and y
    wg = np.bincount(g, weights=w, minlength=G_abs)
    ybar_g = np.bincount(g, weights=ysum, minlength=G_abs) / wg
    xbar_g = np.column_stack([np.bincount(g, weights=w * X[:, j], minlength=G_abs) / wg
                              for j in range(k)]) if k else np.zeros((G_abs, 0))
    Xt = X - xbar_g[g]
    ybar = ybar_g[g]

    XtWX = Xt.T @ (Xt * w[:, None])
    B = np.linalg.pinv(XtWX)
    beta = B @ (Xt.T @ (ysum - w * ybar))
    fit = ybar + Xt @ beta                 # fitted value for every transfer in the cell
    rsum = ysum - w * fit                  # sum over transfers in the cell of w_i * e_i

    N = float(nobs if nobs is not None else d[W].sum())
    K = k + G_abs                          # parameters incl. absorbed effects / constant
    out = {"beta": beta, "nobs": N, "ncells": len(d), "k": k, "n_absorbed": G_abs}

    if cluster is not None:
        c = pd.factorize(d[cluster])[0]
        G = c.max() + 1
        S = np.column_stack([np.bincount(c, weights=Xt[:, j] * rsum, minlength=G) for j in range(k)])
        meat = S.T @ S
        Kc = k + 1                         # absorbed FE nested in clusters are not counted (Stata convention)
        V = B @ meat @ B * (G / (G - 1)) * ((N - 1) / (N - Kc))
        out.update(se=np.sqrt(np.diag(V)), V=V, nclusters=G, se_type=f"cluster({cluster})")
    elif hc1:
        n1 = ysum
        n0 = w - ysum
        q = n1 * (1 - fit) ** 2 + n0 * fit ** 2
        meat = Xt.T @ (Xt * q[:, None])
        V = B @ meat @ B * (N / (N - K))
        out.update(se=np.sqrt(np.diag(V)), V=V, nclusters=None, se_type="HC1")
    else:
        raise ValueError("choose cluster=... or hc1=True")

    if absorb is None:                     # recover the constant
        out["const"] = ybar_g[0] - xbar_g[0] @ beta
    out["xcols"] = list(xcols)
    out["mean_y"] = ysum.sum() / w.sum()
    return out


def add_dummies(df, col, levels, prefix):
    """Add 0/1 dummies for `levels` of `col` (omitted category = any level not listed)."""
    names = []
    for lv in levels:
        nm = f"{prefix}{lv}"
        df[nm] = (df[col] == lv).astype(float)
        names.append(nm)
    return names


def summarize(res, scale=100.0):
    """Coefficients and SEs in percentage points."""
    return pd.DataFrame({"term": res["xcols"], "coef_pp": res["beta"] * scale,
                         "se_pp": res["se"] * scale, "t": res["beta"] / res["se"]})

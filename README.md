# The Round-Dollar Signature — Replication Package

Replication code and data for *"The Round-Dollar Signature: A Label-Free Marker of Payment-Like Stablecoin Transfers."*

This package reproduces every table and figure in the paper and online supplement. All analysis uses the **public** `bigquery-public-data.crypto_ethereum` dataset on Google BigQuery — no proprietary data and no address labels are used, so every result is independently verifiable from the SQL below.

## Setting

Three USD stablecoins on Ethereum mainnet, calendar year 2025: **USDT** (`0xdac1…1ec7`), **USDC** (`0xa0b8…eb48`), **PYUSD** (`0x6c3e…a0e8`); all six-decimal ERC-20 tokens. A transfer is a *whole dollar* when its integer base-unit value is a multiple of 1,000,000.

## Repository structure

```
queries/   01–07  BigQuery SQL (run in the BigQuery console; export CSV to data/)
data/      01–07  query outputs (provided so the code runs without BigQuery access)
code/             lpm.py, lpm_interact.py (Table 1 + S4), make_figs.py (Figures 1–3)
figures/          generated figures (pdf/png) and table1_lpm.csv
```

## Reproduce

```bash
pip install pandas numpy matplotlib
cd code
python lpm.py            # Table 1 (LPM, HC1 SEs)  -> ../figures/table1_lpm.csv
python lpm_interact.py   # Supplement S4 (issuer x size interaction FE)
python make_figs.py      # Figures 1-3 (pdf + png) -> ../figures/
```

To regenerate the data from source, run each file in `queries/` in the BigQuery console and export the result as CSV into `data/` using the filename in each query header. Query 06 (exact simple-transfer) and 07 are the largest; all fit within BigQuery's 1 TB/month free tier.

## Query → exhibit map

| Query | Output | Used in |
|---|---|---|
| 01 | data/01_aggregate.csv | Figure 1 |
| 02 | data/02_single_multi.csv | Figure 1 / text |
| 03 | data/03_size_stratified.csv | Figure 2, Table 1, Supplement S4 |
| 04 | data/04_placebo.csv | Figure 3, Supplement S3 |
| 05 | data/05_stability.csv | Supplement S2 |
| 06 | data/06_exact_simple.csv | Supplement S1 |
| 07 | data/07_exclude_zero_address.csv | Supplement S5 (mint/burn robustness) |

## Revision analyses (round 1)

Additional exhibits requested in peer review. Run order and cost notes: `REVISION_RUNBOOK_KO.md`.

| Query / script | Output | Purpose |
|---|---|---|
| `code/build_labels.py` | `data/labels_eth_mainnet.csv` | Categorised Etherscan name tags (from dawsbot/eth-labels, MIT, commit d9b21ae): payment processors, issuers, exchanges, DeFi/bridges/MEV, other |
| R00 | (metadata) | Column check for Tron/Polygon `logs`; freshness of `crypto_ethereum.contracts` |
| R01 | table `eth_cells2025` | Single scan of 2025 transfers -> day-level cells with call type (direct wallet call vs contract-mediated), EOA/contract status, counterparty label, high-volume-address flag |
| R02a | `data/R02a_cells_day.csv` | Day x coin x type x size cells (Table 1 columns 1–3) |
| R02b | `data/R02b_cells_attr.csv` | Month x attribute cells (Tables S6, S8, S9 Panels A–B) |
| R02c | `data/R02c_cells_day_endpoint.csv` | Day cells excluding mint/burn, by endpoint type (Table 1 column 4, Table 2 Panel A, Table S7) |
| R03 | `data/R03_tron_cells.csv` | Tron USDT replication, calendar 2025 (Table 2, Figure 3, Tables S3, S10) |
| R04 (optional, not run) | `data/R04_polygon_cells.csv` | Polygon USDC/USDT replication |
| R05 | `data/R05_psp_by_address.csv` | Inflows to payment-processor addresses by address (Table S9 Panels C–D) |
| `code/cellreg.py` | — | Exact transfer-level OLS/WLS from cell totals; HC1 and cluster-robust SEs; absorbed FE |
| `code/test_cellreg.py` | — | Reproduces the original Table 1 and matches transfer-level OLS/WLS on simulated data |
| `code/rev_tables.py` | `figures/rev/T1–T6`, `revision_results.md` | Revised Table 1, robustness, label composition, value weighting, cross-chain, endpoint decomposition |
| `code/rev_tables_extra.py` | `figures/rev/T7–T9` | Value-weighted sensitivity, processor leave-one-out, S5/S7 count reconciliation |
| `code/make_figs.py` | `figures/fig1–3` | Figures 1–3 (Figure 3 includes Tron when R03 output is present) |

Because every regressor is constant within a cell, the transfer-level LPM is recovered exactly from
cell totals (n, n_whole, USD value, USD value of whole-dollar transfers); `test_cellreg.py` verifies
this against micro-level OLS, including day-clustered standard errors and absorbed fixed effects.

Reproduce the revision exhibits from the provided data (no BigQuery access needed):

```bash
pip install pandas numpy matplotlib statsmodels
cd code
python test_cellreg.py && python rev_tables.py && python rev_tables_extra.py && python make_figs.py
```

## Citation

If you use this package, please cite the paper (citation to be added upon publication) and this repository.

## License

Code and documentation released under the MIT License (see `LICENSE`).

## Disclosure

AI tools (Claude, Anthropic) were used for code testing and editing.

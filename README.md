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

## Citation

If you use this package, please cite the paper (citation to be added upon publication) and this repository.

## License

Code and documentation released under the MIT License (see `LICENSE`).

## Disclosure

AI tools (Claude, Anthropic) were used for code testing and editing.

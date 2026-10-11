-- R02b (revision): month-level attribute cells for robustness and label-based validation (2025).
-- Reads only the small R01 cell table (near-zero cost). Output -> data/R02b_cells_attr.csv
-- If the console's local CSV download is unavailable because of size, use "Save results" ->
-- "CSV (Google Drive)".
SELECT
  EXTRACT(MONTH FROM dt) AS month,
  coin, tx_type, size_bucket, direct_call, from_contract, to_contract, cpty_cat, cpty_dir, hv,
  SUM(n)       AS n,
  SUM(n_whole) AS n_whole,
  SUM(n_cent)  AS n_cent,
  SUM(n_x99)   AS n_x99,
  SUM(n_half)  AS n_half,
  CAST(SUM(sum_amt) AS STRING)       AS sum_amt,
  CAST(SUM(sum_amt_whole) AS STRING) AS sum_amt_whole
FROM `YOUR_PROJECT.rds_revision.eth_cells2025`
GROUP BY month, coin, tx_type, size_bucket, direct_call, from_contract, to_contract,
         cpty_cat, cpty_dir, hv
ORDER BY month, coin, tx_type, size_bucket;

-- R02a (revision): day-level cells, coin x single/multi x size bucket x calendar day (2025).
-- Reads only the small R01 cell table (near-zero cost). Output -> data/R02a_cells_day.csv (~15,000 rows).
-- Used for: revised Table 1 (day FE, issuer x size x day FE, day-clustered SEs)
--           and count- vs value-weighted whole-dollar shares (Referee 4).
SELECT
  dt, coin, tx_type, size_bucket,
  SUM(n)       AS n,
  SUM(n_whole) AS n_whole,
  SUM(n_cent)  AS n_cent,
  CAST(SUM(sum_amt) AS STRING)       AS sum_amt,
  CAST(SUM(sum_amt_whole) AS STRING) AS sum_amt_whole
FROM `YOUR_PROJECT.rds_revision.eth_cells2025`
GROUP BY dt, coin, tx_type, size_bucket
ORDER BY dt, coin, tx_type, size_bucket;

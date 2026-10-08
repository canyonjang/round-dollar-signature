-- R02c (revision): day-level cells EXCLUDING mint/burn, split by endpoint type (2025).
-- Reads only the small R01 cell table (near-zero cost). Output -> data/R02c_cells_day_endpoint.csv
-- Why: (1) value-weighted shares must exclude mint/burn — on 2025-10-15 a single erroneous PYUSD
--          mint and burn of about $300 trillion each dominates any USD-weighted statistic;
--      (2) day-clustered decomposition of the single-vs-multi contrast by endpoint type:
--          eoa_nonhub = sender and recipient are externally owned accounts (no contract code) and
--                       neither is among the 1,000 most active senders/recipients;
--          other      = everything else (a contract endpoint or a high-volume hub address).
SELECT
  dt, coin, tx_type, size_bucket,
  IF(NOT from_contract AND NOT to_contract AND NOT hv, 'eoa_nonhub', 'other') AS endpoint,
  SUM(n)       AS n,
  SUM(n_whole) AS n_whole,
  SUM(n_cent)  AS n_cent,
  CAST(SUM(sum_amt) AS STRING)       AS sum_amt,
  CAST(SUM(sum_amt_whole) AS STRING) AS sum_amt_whole
FROM `YOUR_PROJECT.rds_revision.eth_cells2025`
WHERE cpty_cat != 'mint_burn'
GROUP BY dt, coin, tx_type, size_bucket, endpoint
ORDER BY dt, coin, tx_type, size_bucket, endpoint;

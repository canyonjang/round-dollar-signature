-- R05 (revision): payment-processor inflows by individual labelled address (Ethereum, 2025).
-- Purpose: show that the low whole-dollar share of transfers into payment-processor addresses
-- (Table 2, Panel B) is not driven by one or two large processors (leave-one-out sensitivity).
-- Output -> data/R05_psp_by_address.csv  (at most 42 addresses x 2 classes x 7 size buckets)
-- Definitions identical to R01: 2025, value > 0, single = exactly one transfer of the three tokens
-- in the transaction. Scans token_transfers once (no transactions/contracts tables); check the
-- dry-run estimate before running.
WITH psp AS (
  SELECT LOWER(TRIM(address)) AS a, ANY_VALUE(name_tag) AS name_tag
  FROM `YOUR_PROJECT.rds_revision.labels_eth`
  WHERE category = 'psp'
  GROUP BY 1
),
st AS (
  SELECT transaction_hash, to_address, SAFE_CAST(value AS NUMERIC) / 1000000 AS amt
  FROM `bigquery-public-data.crypto_ethereum.token_transfers`
  WHERE token_address IN (
      '0xdac17f958d2ee523a2206206994597c13d831ec7',   -- USDT
      '0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48',   -- USDC
      '0x6c3ea9036406852006290770bedfcaba0e23a0e8')   -- PYUSD
    AND block_timestamp >= TIMESTAMP('2025-01-01')
    AND block_timestamp <  TIMESTAMP('2026-01-01')
    AND SAFE_CAST(value AS NUMERIC) > 0
),
psp_tx AS (
  SELECT DISTINCT s.transaction_hash FROM st s JOIN psp p ON s.to_address = p.a
),
cnt AS (
  SELECT transaction_hash, COUNT(*) AS n_sc
  FROM st JOIN psp_tx USING (transaction_hash)
  GROUP BY transaction_hash
)
SELECT
  p.a AS address,
  p.name_tag,
  IF(c.n_sc = 1, '1_single', '2_multi') AS tx_type,
  CASE WHEN s.amt < 1 THEN '0_sub1' WHEN s.amt < 10 THEN '1_1-10' WHEN s.amt < 100 THEN '2_10-100'
       WHEN s.amt < 1000 THEN '3_100-1k' WHEN s.amt < 10000 THEN '4_1k-10k'
       WHEN s.amt < 100000 THEN '5_10k-100k' ELSE '6_100k+' END AS size_bucket,
  COUNT(*)                        AS n,
  COUNTIF(MOD(s.amt, 1) = 0)      AS n_whole,
  COUNTIF(MOD(s.amt * 100, 1) = 0) AS n_cent
FROM st s
JOIN psp p ON s.to_address = p.a
JOIN cnt c USING (transaction_hash)
GROUP BY address, name_tag, tx_type, size_bucket
ORDER BY address, tx_type, size_bucket;

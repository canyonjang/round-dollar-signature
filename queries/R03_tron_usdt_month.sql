-- R03 (revision): cross-chain replication on TRON (low-fee, retail-heavy), USDT TRC-20, one month.
-- Output -> data/R03_tron_cells.csv
-- Cost control: the Google Tron tables are partitioned by MONTH, so one calendar month is the
-- smallest unit you can be billed for. Check the dry-run estimate; to add months, widen the
-- block_timestamp range (each month adds roughly the same number of bytes).
-- Format notes (check with R00 / table PREVIEW): Tron addresses are stored in lowercase; the
-- USDT contract TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t is hex a614f803b6fd780986a42c78ec9c7f77e6ded13c
-- (possibly with a '0x' or '41' prefix), so ENDS_WITH is used to match any of these forms.
-- TRC-20 Transfer events use the same topic0 as ERC-20. USDT on Tron has 6 decimals.
-- Definitions identical to the Ethereum queries: single = exactly one USDT Transfer event in the
-- transaction; whole dollar = base-unit value is a multiple of 1,000,000.
WITH lg AS (
  SELECT
    transaction_hash,
    REGEXP_REPLACE(LOWER(data), r'^0x', '') AS d
  FROM `bigquery-public-data.goog_blockchain_tron_mainnet_us.logs`
  WHERE block_timestamp >= TIMESTAMP('2025-06-01')
    AND block_timestamp <  TIMESTAMP('2025-07-01')
    AND ENDS_WITH(LOWER(address), 'a614f803b6fd780986a42c78ec9c7f77e6ded13c')
    AND ENDS_WITH(LOWER(topics[SAFE_OFFSET(0)]),
                  'ddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef')
    AND ARRAY_LENGTH(topics) = 3                      -- standard Transfer(from, to, value)
),
st AS (
  SELECT
    transaction_hash,
    -- uint256 amount in the 32-byte data word; values above 2^63 base units (> 9.2 trillion USDT)
    -- cannot occur and would be dropped by SAFE_CAST
    SAFE_CAST(CONCAT('0x', NULLIF(LTRIM(SUBSTR(d, -64), '0'), '')) AS INT64) AS v
  FROM lg
),
st2 AS (SELECT * FROM st WHERE v > 0),
txn AS (SELECT transaction_hash, COUNT(*) AS n_sc FROM st2 GROUP BY transaction_hash)
SELECT
  'TRON' AS chain,
  'USDT' AS coin,
  IF(t.n_sc = 1, '1_single', '2_multi') AS tx_type,
  CASE WHEN v < 1000000 THEN '0_sub1' WHEN v < 10000000 THEN '1_1-10' WHEN v < 100000000 THEN '2_10-100'
       WHEN v < 1000000000 THEN '3_100-1k' WHEN v < 10000000000 THEN '4_1k-10k'
       WHEN v < 100000000000 THEN '5_10k-100k' ELSE '6_100k+' END AS size_bucket,
  COUNT(*)                              AS n,
  COUNTIF(MOD(v, 1000000) = 0)          AS n_whole,
  COUNTIF(MOD(v, 10000) = 0)            AS n_cent,
  COUNTIF(MOD(v, 1000000) = 500000)     AS n_half,
  COUNTIF(MOD(v, 1000000) = 370000)     AS n_37,
  COUNTIF(MOD(v, 1000000) = 123456)     AS n_123456,
  CAST(SUM(CAST(v AS NUMERIC)) / 1000000 AS STRING) AS sum_amt,
  CAST(SUM(IF(MOD(v, 1000000) = 0, CAST(v AS NUMERIC), 0)) / 1000000 AS STRING) AS sum_amt_whole
FROM st2 s JOIN txn t USING (transaction_hash)
GROUP BY chain, coin, tx_type, size_bucket
ORDER BY tx_type, size_bucket;

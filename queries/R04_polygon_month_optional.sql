-- R04 (revision, OPTIONAL): second low-fee replication on POLYGON PoS, native USDC and USDT, one month.
-- Run only if R03 was affordable; it adds USDC on a low-fee chain (Referee 3 cites USDC on L2s).
-- Output -> data/R04_polygon_cells.csv
-- Monthly partitions: one calendar month is the minimum billing unit. Check the dry-run estimate.
-- Native USDC 0x3c499c542cef5e3811e1192ce70d8cc03d5c3359 and USDT 0xc2132d05d31c914a87c6611c10748aeb04b58e8f
-- both have 6 decimals. single = exactly one Transfer of these two tokens in the transaction.
WITH lg AS (
  SELECT
    transaction_hash,
    CASE
      WHEN ENDS_WITH(LOWER(address), '3c499c542cef5e3811e1192ce70d8cc03d5c3359') THEN 'USDC'
      WHEN ENDS_WITH(LOWER(address), 'c2132d05d31c914a87c6611c10748aeb04b58e8f') THEN 'USDT' END AS coin,
    REGEXP_REPLACE(LOWER(data), r'^0x', '') AS d
  FROM `bigquery-public-data.goog_blockchain_polygon_mainnet_us.logs`
  WHERE block_timestamp >= TIMESTAMP('2025-06-01')
    AND block_timestamp <  TIMESTAMP('2025-07-01')
    AND (ENDS_WITH(LOWER(address), '3c499c542cef5e3811e1192ce70d8cc03d5c3359')
         OR ENDS_WITH(LOWER(address), 'c2132d05d31c914a87c6611c10748aeb04b58e8f'))
    AND ENDS_WITH(LOWER(topics[SAFE_OFFSET(0)]),
                  'ddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef')
    AND ARRAY_LENGTH(topics) = 3
),
st AS (
  SELECT transaction_hash, coin,
         SAFE_CAST(CONCAT('0x', NULLIF(LTRIM(SUBSTR(d, -64), '0'), '')) AS INT64) AS v
  FROM lg
),
st2 AS (SELECT * FROM st WHERE v > 0),
txn AS (SELECT transaction_hash, COUNT(*) AS n_sc FROM st2 GROUP BY transaction_hash)
SELECT
  'POLYGON' AS chain,
  coin,
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
ORDER BY coin, tx_type, size_bucket;

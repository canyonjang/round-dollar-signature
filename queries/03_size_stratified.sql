-- Q3: whole-dollar share by coin x single/multi x size bucket (2025). -> data/03_size_stratified.csv
WITH st AS (
  SELECT token_address, transaction_hash, SAFE_CAST(value AS NUMERIC)/1000000 AS amt
  FROM `bigquery-public-data.crypto_ethereum.token_transfers`
  WHERE token_address IN (
      '0xdac17f958d2ee523a2206206994597c13d831ec7',
      '0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48',
      '0x6c3ea9036406852006290770bedfcaba0e23a0e8')
    AND block_timestamp >= TIMESTAMP('2025-01-01')
    AND block_timestamp <  TIMESTAMP('2026-01-01')
    AND SAFE_CAST(value AS NUMERIC) > 0
),
txn AS (SELECT transaction_hash, COUNT(*) AS n_sc_transfers FROM st GROUP BY transaction_hash)
SELECT
  CASE s.token_address
    WHEN '0xdac17f958d2ee523a2206206994597c13d831ec7' THEN 'USDT'
    WHEN '0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48' THEN 'USDC'
    WHEN '0x6c3ea9036406852006290770bedfcaba0e23a0e8' THEN 'PYUSD' END AS coin,
  IF(t.n_sc_transfers=1,'1_single','2_multi') AS tx_type,
  CASE WHEN s.amt<1 THEN '0_sub1' WHEN s.amt<10 THEN '1_1-10' WHEN s.amt<100 THEN '2_10-100'
       WHEN s.amt<1000 THEN '3_100-1k' WHEN s.amt<10000 THEN '4_1k-10k'
       WHEN s.amt<100000 THEN '5_10k-100k' ELSE '6_100k+' END AS size_bucket,
  COUNT(*) AS n,
  ROUND(AVG(IF(MOD(s.amt,1)=0,1,0))*100,2) AS pct_whole_dollar
FROM st s JOIN txn t USING (transaction_hash)
GROUP BY coin, tx_type, size_bucket ORDER BY coin, tx_type, size_bucket;

-- Q5: whole-dollar share by year x coin x single/multi (2023-2025). -> data/05_stability.csv
WITH st AS (
  SELECT token_address, transaction_hash, EXTRACT(YEAR FROM block_timestamp) AS yr,
         SAFE_CAST(value AS NUMERIC)/1000000 AS amt
  FROM `bigquery-public-data.crypto_ethereum.token_transfers`
  WHERE token_address IN (
      '0xdac17f958d2ee523a2206206994597c13d831ec7',
      '0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48',
      '0x6c3ea9036406852006290770bedfcaba0e23a0e8')
    AND block_timestamp >= TIMESTAMP('2023-01-01')
    AND block_timestamp <  TIMESTAMP('2026-01-01')
    AND SAFE_CAST(value AS NUMERIC) > 0
),
txn AS (SELECT transaction_hash, COUNT(*) AS n_sc FROM st GROUP BY transaction_hash)
SELECT s.yr,
  CASE s.token_address
    WHEN '0xdac17f958d2ee523a2206206994597c13d831ec7' THEN 'USDT'
    WHEN '0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48' THEN 'USDC'
    WHEN '0x6c3ea9036406852006290770bedfcaba0e23a0e8' THEN 'PYUSD' END AS coin,
  IF(t.n_sc=1,'1_single','2_multi') AS tx_type, COUNT(*) AS n_total,
  COUNTIF(MOD(s.amt,1)=0) AS n_whole_dollar,
  ROUND(AVG(IF(MOD(s.amt,1)=0,1,0))*100,3) AS pct_whole_dollar
FROM st s JOIN txn t USING (transaction_hash)
GROUP BY s.yr, coin, tx_type ORDER BY coin, tx_type, s.yr;

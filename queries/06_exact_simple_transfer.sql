-- Q6: exact simple-transfer (total logs = 1) vs complex, round shares (2025). -> data/06_exact_simple.csv
-- NOTE: largest query (scans full 2025 logs table); check estimated bytes before running.
WITH sc AS (
  SELECT
    CASE token_address
      WHEN '0xdac17f958d2ee523a2206206994597c13d831ec7' THEN 'USDT'
      WHEN '0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48' THEN 'USDC'
      WHEN '0x6c3ea9036406852006290770bedfcaba0e23a0e8' THEN 'PYUSD' END AS coin,
    transaction_hash, SAFE_CAST(value AS NUMERIC)/1000000 AS amt
  FROM `bigquery-public-data.crypto_ethereum.token_transfers`
  WHERE token_address IN (
      '0xdac17f958d2ee523a2206206994597c13d831ec7',
      '0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48',
      '0x6c3ea9036406852006290770bedfcaba0e23a0e8')
    AND block_timestamp >= TIMESTAMP('2025-01-01')
    AND block_timestamp <  TIMESTAMP('2026-01-01')
    AND SAFE_CAST(value AS NUMERIC) > 0
),
logcnt AS (
  SELECT transaction_hash, COUNT(*) AS n_logs
  FROM `bigquery-public-data.crypto_ethereum.logs`
  WHERE block_timestamp >= TIMESTAMP('2025-01-01')
    AND block_timestamp <  TIMESTAMP('2026-01-01')
  GROUP BY transaction_hash
)
SELECT s.coin, IF(l.n_logs=1,'1_simple_exact','2_complex_exact') AS exact_class,
  COUNT(*) AS n_transfers,
  ROUND(AVG(IF(MOD(s.amt,1)=0,1,0))*100,3)   AS pct_whole_dollar,
  ROUND(AVG(IF(MOD(s.amt,10)=0,1,0))*100,3)  AS pct_mult_10,
  ROUND(AVG(IF(MOD(s.amt,100)=0,1,0))*100,3) AS pct_mult_100
FROM sc s JOIN logcnt l USING (transaction_hash)
GROUP BY s.coin, exact_class ORDER BY s.coin, exact_class;

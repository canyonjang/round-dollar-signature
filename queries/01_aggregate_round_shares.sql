-- Q1: aggregate round-number shares by stablecoin (2025). Output -> data/01_aggregate.csv
WITH base AS (
  SELECT
    CASE token_address
      WHEN '0xdac17f958d2ee523a2206206994597c13d831ec7' THEN 'USDT'
      WHEN '0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48' THEN 'USDC'
      WHEN '0x6c3ea9036406852006290770bedfcaba0e23a0e8' THEN 'PYUSD'
    END AS coin,
    SAFE_CAST(value AS NUMERIC)/1000000 AS amt          -- all three tokens use 6 decimals
  FROM `bigquery-public-data.crypto_ethereum.token_transfers`
  WHERE token_address IN (
      '0xdac17f958d2ee523a2206206994597c13d831ec7',
      '0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48',
      '0x6c3ea9036406852006290770bedfcaba0e23a0e8')
    AND block_timestamp >= TIMESTAMP('2025-01-01')
    AND block_timestamp <  TIMESTAMP('2026-01-01')
    AND SAFE_CAST(value AS NUMERIC) > 0
)
SELECT coin, COUNT(*) AS n_transfers,
  ROUND(AVG(IF(MOD(amt,1)=0,1,0))*100,2)    AS pct_whole_dollar,
  ROUND(AVG(IF(MOD(amt,10)=0,1,0))*100,2)   AS pct_mult_10,
  ROUND(AVG(IF(MOD(amt,100)=0,1,0))*100,2)  AS pct_mult_100,
  ROUND(AVG(IF(MOD(amt,1000)=0,1,0))*100,2) AS pct_mult_1000
FROM base WHERE coin IS NOT NULL GROUP BY coin ORDER BY coin;

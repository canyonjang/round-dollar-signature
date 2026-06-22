-- Q4: placebo-digit test, share at selected sub-dollar residues (2025). -> data/04_placebo.csv
WITH st AS (
  SELECT token_address, transaction_hash, SAFE_CAST(value AS NUMERIC) AS v
  FROM `bigquery-public-data.crypto_ethereum.token_transfers`
  WHERE token_address IN (
      '0xdac17f958d2ee523a2206206994597c13d831ec7',
      '0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48',
      '0x6c3ea9036406852006290770bedfcaba0e23a0e8')
    AND block_timestamp >= TIMESTAMP('2025-01-01')
    AND block_timestamp <  TIMESTAMP('2026-01-01')
    AND SAFE_CAST(value AS NUMERIC) > 0
),
txn AS (SELECT transaction_hash, COUNT(*) AS n FROM st GROUP BY transaction_hash)
SELECT
  CASE s.token_address
    WHEN '0xdac17f958d2ee523a2206206994597c13d831ec7' THEN 'USDT'
    WHEN '0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48' THEN 'USDC'
    WHEN '0x6c3ea9036406852006290770bedfcaba0e23a0e8' THEN 'PYUSD' END AS coin,
  IF(t.n=1,'1_single','2_multi') AS tx_type, COUNT(*) AS n_total,
  ROUND(COUNTIF(MOD(s.v,1000000)=0)     /COUNT(*)*100,4) AS pct_resid_000000_whole,
  ROUND(COUNTIF(MOD(s.v,1000000)=500000)/COUNT(*)*100,4) AS pct_resid_500000_half,
  ROUND(COUNTIF(MOD(s.v,1000000)=370000)/COUNT(*)*100,4) AS pct_resid_370000_placebo,
  ROUND(COUNTIF(MOD(s.v,1000000)=123456)/COUNT(*)*100,4) AS pct_resid_123456_placebo
FROM st s JOIN txn t USING (transaction_hash)
GROUP BY coin, tx_type ORDER BY coin, tx_type;

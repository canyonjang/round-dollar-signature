-- R01 (revision): the ONLY expensive Ethereum query. Scans 2025 USDT/USDC/PYUSD transfers once and
-- stores day-level attribute cells (a few million rows, well under 1 GB), so R02a/R02b cost almost
-- nothing and the table also fits the BigQuery sandbox (10 GB storage).
-- Before running:
--   1. replace YOUR_PROJECT; create dataset `rds_revision` (location: US)
--   2. upload data/labels_eth_mainnet.csv as table `rds_revision.labels_eth`
--      (do NOT auto-detect: schema address:STRING,category:STRING,name_tag:STRING; header row = 1)
--   3. set "Maximum bytes billed" in Query settings and check the dry-run estimate
--
-- Sample definition identical to queries 01-07: 2025, value > 0; single = exactly one transfer of
-- these three tokens in the transaction; whole dollar = value is a multiple of 1,000,000 base units.
-- Per-transfer attributes (public data):
--   direct_call   : the transaction's top-level `to` is the token contract (plain wallet transfer)
--   from_contract : sender is a deployed contract (router, pool, Safe multisig, ...)
--   to_contract   : recipient is a deployed contract
--   cpty_cat      : highest-priority label of sender/recipient (eth-labels / Etherscan tags):
--                   mint_burn > psp > issuer > cex > defi > other > unlabeled
--   cpty_dir      : which side carries that label: 'to', 'from', 'both', 'none'
--   hv            : sender among the 1,000 most active senders or recipient among the 1,000 most
--                   active recipients in this sample (label-free proxy for hot wallets / bots)
-- No PARTITION BY on purpose: in the BigQuery sandbox, partitions older than 60 days expire
-- immediately, which would silently empty a table of 2025 data. The table is small anyway.
CREATE OR REPLACE TABLE `YOUR_PROJECT.rds_revision.eth_cells2025`
CLUSTER BY coin, tx_type
AS
WITH st AS (
  SELECT
    DATE(block_timestamp) AS dt,
    token_address,
    transaction_hash,
    from_address,
    to_address,
    SAFE_CAST(value AS NUMERIC) / 1000000 AS amt          -- all three tokens use 6 decimals
  FROM `bigquery-public-data.crypto_ethereum.token_transfers`
  WHERE token_address IN (
      '0xdac17f958d2ee523a2206206994597c13d831ec7',   -- USDT
      '0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48',   -- USDC
      '0x6c3ea9036406852006290770bedfcaba0e23a0e8')   -- PYUSD
    AND block_timestamp >= TIMESTAMP('2025-01-01')
    AND block_timestamp <  TIMESTAMP('2026-01-01')
    AND SAFE_CAST(value AS NUMERIC) > 0
),
txn AS (
  SELECT transaction_hash, COUNT(*) AS n_sc FROM st GROUP BY transaction_hash
),
tx AS (
  SELECT `hash` AS transaction_hash, to_address AS tx_to
  FROM `bigquery-public-data.crypto_ethereum.transactions`
  WHERE block_timestamp >= TIMESTAMP('2025-01-01')
    AND block_timestamp <  TIMESTAMP('2026-01-01')
),
ca AS (
  SELECT DISTINCT address FROM `bigquery-public-data.crypto_ethereum.contracts`
),
lab AS (
  SELECT LOWER(TRIM(address)) AS address, ANY_VALUE(category) AS category
  FROM `YOUR_PROJECT.rds_revision.labels_eth`
  GROUP BY 1
),
hv_from AS (
  SELECT from_address AS a FROM st
  WHERE from_address != '0x0000000000000000000000000000000000000000'
  GROUP BY from_address ORDER BY COUNT(*) DESC LIMIT 1000
),
hv_to AS (
  SELECT to_address AS a FROM st
  WHERE to_address != '0x0000000000000000000000000000000000000000'
  GROUP BY to_address ORDER BY COUNT(*) DESC LIMIT 1000
),
x AS (
  SELECT
    s.dt,
    CASE s.token_address
      WHEN '0xdac17f958d2ee523a2206206994597c13d831ec7' THEN 'USDT'
      WHEN '0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48' THEN 'USDC'
      WHEN '0x6c3ea9036406852006290770bedfcaba0e23a0e8' THEN 'PYUSD' END AS coin,
    IF(t.n_sc = 1, '1_single', '2_multi') AS tx_type,
    s.amt,
    IFNULL(tx.tx_to = s.token_address, FALSE) AS direct_call,
    fc.address IS NOT NULL AS from_contract,
    tc.address IS NOT NULL AS to_contract,
    (s.from_address = '0x0000000000000000000000000000000000000000'
     OR s.to_address = '0x0000000000000000000000000000000000000000') AS mint_burn,
    IFNULL(lf.category, '') AS fcat,
    IFNULL(lt.category, '') AS tcat,
    (hf.a IS NOT NULL OR ht.a IS NOT NULL) AS hv
  FROM st s
  JOIN txn t USING (transaction_hash)
  LEFT JOIN tx USING (transaction_hash)
  LEFT JOIN ca fc ON fc.address = s.from_address
  LEFT JOIN ca tc ON tc.address = s.to_address
  LEFT JOIN lab lf ON lf.address = s.from_address
  LEFT JOIN lab lt ON lt.address = s.to_address
  LEFT JOIN hv_from hf ON hf.a = s.from_address
  LEFT JOIN hv_to   ht ON ht.a = s.to_address
),
y AS (
  SELECT *,
    CASE
      WHEN mint_burn THEN 'mint_burn'
      WHEN 'psp'    IN (fcat, tcat) THEN 'psp'
      WHEN 'issuer' IN (fcat, tcat) THEN 'issuer'
      WHEN 'cex'    IN (fcat, tcat) THEN 'cex'
      WHEN 'defi'   IN (fcat, tcat) THEN 'defi'
      WHEN 'other'  IN (fcat, tcat) THEN 'other'
      ELSE 'unlabeled' END AS cpty_cat
  FROM x
)
SELECT
  dt,
  coin,
  tx_type,
  CASE WHEN amt < 1 THEN '0_sub1' WHEN amt < 10 THEN '1_1-10' WHEN amt < 100 THEN '2_10-100'
       WHEN amt < 1000 THEN '3_100-1k' WHEN amt < 10000 THEN '4_1k-10k'
       WHEN amt < 100000 THEN '5_10k-100k' ELSE '6_100k+' END AS size_bucket,
  direct_call,
  from_contract,
  to_contract,
  cpty_cat,
  CASE
    WHEN cpty_cat IN ('mint_burn', 'unlabeled') THEN 'none'
    WHEN fcat = cpty_cat AND tcat = cpty_cat THEN 'both'
    WHEN tcat = cpty_cat THEN 'to'
    ELSE 'from' END AS cpty_dir,
  hv,
  COUNT(*)                                AS n,
  COUNTIF(MOD(amt, 1) = 0)                AS n_whole,
  COUNTIF(MOD(amt * 100, 1) = 0)          AS n_cent,     -- whole-cent (posted-price-like) amounts
  COUNTIF(MOD(amt * 100, 100) = 99)       AS n_x99,      -- $X.99 charm prices
  COUNTIF(MOD(amt, 1) = 0.5)              AS n_half,
  SUM(amt)                                AS sum_amt,
  SUM(IF(MOD(amt, 1) = 0, amt, 0))        AS sum_amt_whole
FROM y
GROUP BY dt, coin, tx_type, size_bucket, direct_call, from_contract, to_contract,
         cpty_cat, cpty_dir, hv;

-- Sanity check (cheap). Must match data/02_single_multi.csv exactly:
-- SELECT coin, tx_type, SUM(n) n, ROUND(SUM(n_whole)/SUM(n)*100, 2) pct_whole
-- FROM `YOUR_PROJECT.rds_revision.eth_cells2025` GROUP BY 1, 2 ORDER BY 1, 2;

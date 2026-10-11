-- R00 (revision): free metadata check before running R03/R04.
-- Confirms the column names/types of the Google Blockchain Analytics `logs` tables
-- (Tron and Polygon tables use MONTHLY partitions on block_timestamp).
-- Expected (adapt R03/R04 if different): address STRING, topics ARRAY<STRING>, data STRING,
--                                       transaction_hash STRING, block_timestamp TIMESTAMP.
SELECT table_schema, column_name, data_type, is_partitioning_column, clustering_ordinal_position
FROM `bigquery-public-data.goog_blockchain_tron_mainnet_us.INFORMATION_SCHEMA.COLUMNS`
WHERE table_name = 'logs'
UNION ALL
SELECT table_schema, column_name, data_type, is_partitioning_column, clustering_ordinal_position
FROM `bigquery-public-data.goog_blockchain_polygon_mainnet_us.INFORMATION_SCHEMA.COLUMNS`
WHERE table_name = 'logs'
ORDER BY table_schema, column_name;

-- To see the raw address/topic/data format for free, open the table in the BigQuery console
-- (bigquery-public-data > goog_blockchain_tron_mainnet_us > logs) and use the PREVIEW tab.
-- Do NOT run a `SELECT ... LIMIT 3` query for this: LIMIT does not reduce the bytes billed.

-- Also check that the Ethereum contracts table (used for EOA/contract status in R01) is current
-- through 2025 (scans one small column; a few GB at most):
SELECT MAX(block_timestamp) AS latest_contract_creation
FROM `bigquery-public-data.crypto_ethereum.contracts`;

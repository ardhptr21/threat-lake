-- ThreatLake gold layer

CREATE NAMESPACE IF NOT EXISTS ${CATALOG}.${NAMESPACE};

CREATE TABLE IF NOT EXISTS ${CATALOG}.${NAMESPACE}.gold_prioritized_vulnerabilities (
  cve_id STRING,
  source STRING,
  published_at STRING,
  vendor STRING,
  product STRING,
  severity STRING,
  cvss_score DOUBLE,
  cwe STRING,
  summary STRING,
  kev_status BOOLEAN,
  exploit_available BOOLEAN,
  advisory_activity INT,
  references_json STRING,
  raw_sources_json STRING,
  extras_json STRING,
  priority_score INT,
  risk_level STRING,
  silver_id STRING,
  bronze_id STRING,
  gold_id STRING,
  gold_at STRING
)
USING iceberg;

-- DROP VIEW IF EXISTS ${CATALOG}.${NAMESPACE}.vulnerability_ranking;
-- CREATE VIEW ${CATALOG}.${NAMESPACE}.vulnerability_ranking AS
-- SELECT
--   cve_id,
--   priority_score,
--   risk_level,
--   severity,
--   kev_status,
--   exploit_available,
--   advisory_activity
-- FROM ${CATALOG}.${NAMESPACE}.gold_prioritized_vulnerabilities;



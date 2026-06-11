-- ThreatLake silver layer

CREATE NAMESPACE IF NOT EXISTS ${CATALOG}.${NAMESPACE};

CREATE TABLE IF NOT EXISTS ${CATALOG}.${NAMESPACE}.silver_vulnerabilities (
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
  silver_id STRING,
  bronze_id STRING,
  silver_at STRING
)
USING iceberg;

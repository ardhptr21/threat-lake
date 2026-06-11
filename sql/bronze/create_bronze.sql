-- ThreatLake bronze layer
-- Replace ${CATALOG} and ${NAMESPACE} with your runtime catalog and namespace.

CREATE NAMESPACE IF NOT EXISTS ${CATALOG}.${NAMESPACE};

CREATE TABLE IF NOT EXISTS ${CATALOG}.${NAMESPACE}.bronze_events (
  bronze_id STRING,
  source STRING,
  source_id STRING,
  topic STRING,
  fetched_at STRING,
  bronze_at STRING,
  payload STRING
)
USING iceberg;


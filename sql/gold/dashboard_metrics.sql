-- ThreatLake executive dashboard metrics

SELECT
  COUNT(*) AS total_cves,
  SUM(CASE WHEN risk_level = 'Critical' THEN 1 ELSE 0 END) AS critical_cves,
  SUM(CASE WHEN kev_status THEN 1 ELSE 0 END) AS exploited_vulnerabilities,
  AVG(priority_score) AS avg_priority_score
FROM ${CATALOG}.${NAMESPACE}.gold_prioritized_vulnerabilities;


# Dashboard Queries

Use these against the gold layer for Superset datasets.

## Executive overview

```sql
SELECT
  COUNT(*) AS total_cves,
  SUM(CASE WHEN risk_level = 'Critical' THEN 1 ELSE 0 END) AS critical_cves,
  SUM(CASE WHEN kev_status THEN 1 ELSE 0 END) AS exploited_vulnerabilities,
  AVG(priority_score) AS average_priority_score
FROM gold_prioritized_vulnerabilities;
```

## Vendor risk ranking

```sql
SELECT
  COALESCE(vendor, 'Unknown') AS vendor,
  COUNT(*) AS vulnerability_count,
  AVG(priority_score) AS avg_priority_score
FROM gold_prioritized_vulnerabilities
GROUP BY 1
ORDER BY avg_priority_score DESC, vulnerability_count DESC;
```

## Monthly trend

```sql
SELECT
  date_trunc('month', CAST(published_at AS timestamp)) AS month,
  COUNT(*) AS total_cves
FROM gold_prioritized_vulnerabilities
GROUP BY 1
ORDER BY 1;
```


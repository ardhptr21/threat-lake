from __future__ import annotations

import os
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from trino.dbapi import connect
from trino.auth import BasicAuthentication

app = FastAPI(title="ThreatLake API")

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

TRINO_HOST = os.getenv("TRINO_HOST", "trino")
TRINO_PORT = int(os.getenv("TRINO_PORT", "8080"))
TRINO_USER = os.getenv("TRINO_USER", "admin")
TRINO_CATALOG = os.getenv("TRINO_CATALOG", "iceberg")
TRINO_SCHEMA = os.getenv("TRINO_SCHEMA", "default")

def get_trino_connection():
    return connect(
        host=TRINO_HOST,
        port=TRINO_PORT,
        user=TRINO_USER,
        catalog=TRINO_CATALOG,
        schema=TRINO_SCHEMA,
    )

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/api/metrics")
def get_metrics():
    try:
        conn = get_trino_connection()
        cur = conn.cursor()
        query = f"""
        SELECT
          COUNT(*) AS total_cves,
          SUM(CASE WHEN risk_level = 'Critical' THEN 1 ELSE 0 END) AS critical_cves,
          SUM(CASE WHEN kev_status THEN 1 ELSE 0 END) AS exploited_vulnerabilities,
          AVG(priority_score) AS avg_priority_score
        FROM {TRINO_CATALOG}.{TRINO_SCHEMA}.gold_prioritized_vulnerabilities
        """
        cur.execute(query)
        res = cur.fetchone()
        if not res:
            return {"total_cves": 0, "critical_cves": 0, "exploited_vulnerabilities": 0, "avg_priority_score": 0}
        
        return {
            "total_cves": res[0] or 0,
            "critical_cves": res[1] or 0,
            "exploited_vulnerabilities": res[2] or 0,
            "avg_priority_score": round(res[3] or 0, 2)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/vulnerabilities")
def get_vulnerabilities(limit: int = 50):
    try:
        conn = get_trino_connection()
        cur = conn.cursor()
        query = f"""
        SELECT
          cve_id,
          priority_score,
          risk_level,
          severity,
          kev_status,
          exploit_available,
          advisory_activity,
          source,
          published_at
        FROM {TRINO_CATALOG}.{TRINO_SCHEMA}.gold_prioritized_vulnerabilities
        ORDER BY priority_score DESC, published_at DESC
        LIMIT {limit}
        """
        cur.execute(query)
        rows = cur.fetchall()
        
        columns = [desc[0] for desc in cur.description]
        return [dict(zip(columns, row)) for row in rows]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/sources/summary")
def get_source_summary():
    try:
        conn = get_trino_connection()
        cur = conn.cursor()
        query = f"""
        SELECT source, count(*) as count
        FROM {TRINO_CATALOG}.{TRINO_SCHEMA}.gold_prioritized_vulnerabilities
        GROUP BY source
        """
        cur.execute(query)
        rows = cur.fetchall()
        return [{"source": row[0], "count": row[1]} for row in rows]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

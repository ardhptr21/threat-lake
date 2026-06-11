# ThreatLake

> Multi-Source Cyber Threat Intelligence Data Lakehouse for Vulnerability Prioritization

## Overview

ThreatLake adalah platform Cyber Threat Intelligence (CTI) berbasis Data Lakehouse yang dirancang untuk mengintegrasikan berbagai sumber threat intelligence ke dalam satu platform analitik terpusat.

Sistem ini membantu Security Analyst, SOC Team, dan Vulnerability Management Team dalam menentukan prioritas vulnerability yang harus segera ditangani berdasarkan berbagai indikator risiko dari sumber resmi.

Berbeda dengan vulnerability scanner tradisional yang hanya berfokus pada CVSS Score, ThreatLake menggabungkan informasi dari berbagai sumber untuk memberikan konteks yang lebih lengkap terhadap setiap vulnerability.

---

## Background

Jumlah vulnerability yang dipublikasikan setiap tahun terus meningkat. National Vulnerability Database (NVD) telah mencatat ratusan ribu CVE dan terus bertambah setiap hari.

Dalam praktiknya, organisasi menghadapi beberapa tantangan utama:

* Jumlah CVE yang sangat besar.
* Informasi tersebar pada banyak platform.
* Sulit menentukan vulnerability yang harus diprioritaskan.
* Keterbatasan sumber daya untuk melakukan patching terhadap seluruh vulnerability.

Akibatnya, vulnerability yang sebenarnya sudah dieksploitasi secara aktif sering kali terlambat ditangani.

ThreatLake hadir untuk mengatasi permasalahan tersebut melalui pendekatan Data Lakehouse yang mampu mengumpulkan, menyimpan, mengolah, dan menganalisis data threat intelligence secara terpusat.

---

## Objectives

### Business Objectives

* Membantu organisasi menentukan prioritas vulnerability.
* Mengurangi waktu analisis vulnerability.
* Menyediakan visibilitas terhadap ancaman yang sedang berkembang.
* Mendukung proses patch management.

### Technical Objectives

* Membangun Data Lakehouse berbasis Apache Iceberg.
* Mengimplementasikan pipeline streaming menggunakan Apache Kafka.
* Mengintegrasikan berbagai sumber threat intelligence.
* Menyediakan dashboard analitik real-time.
* Menyimpan data historis untuk kebutuhan analisis jangka panjang.

---

## Data Sources

### National Vulnerability Database (NVD)

Data vulnerability resmi dari NIST.

Data yang digunakan:

* CVE ID
* CVSS Score
* Description
* CWE
* Published Date
* References

API:

```text
https://services.nvd.nist.gov/rest/json/cves/2.0
```

---

### CISA Known Exploited Vulnerabilities (KEV)

Digunakan untuk mengetahui apakah suatu vulnerability telah dieksploitasi secara aktif.

Data:

* CVE ID
* Vendor
* Product
* Due Date
* Notes

---

### GitHub Security Advisories

Digunakan untuk mendapatkan informasi advisory keamanan.

Data:

* Advisory ID
* Severity
* CVE Mapping
* Repository
* Published Date

---

### GitHub Events API

Digunakan untuk menganalisis aktivitas komunitas terhadap vulnerability tertentu.

Data:

* Push Event
* Release Event
* Issue Event
* Pull Request Event

---

### Exploit Database Feed

Digunakan untuk mengetahui ketersediaan exploit publik.

Data:

* CVE ID
* Exploit Title
* Publication Date

---

## Big Data Characteristics (5V)

### Volume

Data berasal dari berbagai sumber:

* 300.000+ CVE historis
* Jutaan GitHub Events
* Security Advisories
* Exploit Feeds

### Velocity

Data diperbarui secara berkala:

* NVD Updates
* GitHub Events
* Security Advisories
* Exploit Feeds

Ingestion dilakukan setiap 5 menit.

### Variety

Berbagai format data:

* JSON
* Event Logs
* Security Advisories
* Threat Intelligence Feeds

### Veracity

Data berasal dari sumber resmi dan terpercaya:

* NIST
* CISA
* GitHub

### Value

Membantu organisasi melakukan vulnerability prioritization secara lebih efektif.

---

## System Architecture

```text
                        +----------------+
                        |    NVD API     |
                        +--------+-------+
                                 |
                        +--------v-------+
                        |    Airflow     |
                        |   Scheduler    |
                        +--------+-------+
                                 |
                                 v

+-----------+      +----------------------+      +-----------+
| CISA KEV  | ---> |      Kafka Bus       | <--- | GitHub    |
+-----------+      +----------+-----------+      +-----------+
                              |
                              |
                              v

                    +----------------------+
                    |  Spark Streaming     |
                    | Processing Pipeline  |
                    +----------+-----------+
                               |
                               v

                    +----------------------+
                    | Apache Iceberg       |
                    | Data Lakehouse       |
                    +----------+-----------+
                               |
              +----------------+----------------+
              |                |                |
              v                v                v

           Bronze           Silver            Gold
         Raw Data       Clean Data       Analytics Data

                               |
                               v

                    +----------------------+
                    |        Trino         |
                    +----------+-----------+
                               |
                               v

                    +----------------------+
                    | Apache Superset      |
                    +----------------------+
```

---

## Data Lakehouse Design

### Bronze Layer

Menyimpan data mentah dari seluruh sumber.

Contoh:

```json
{
  "cve": {
    "id": "CVE-2026-12345"
  }
}
```

Karakteristik:

* Immutable
* Historical
* Raw Data

---

### Silver Layer

Data yang telah dinormalisasi.

Contoh:

```json
{
  "cve_id": "CVE-2026-12345",
  "cvss_score": 9.8,
  "kev_status": true,
  "exploit_available": true
}
```

Karakteristik:

* Cleaned
* Normalized
* Joined Data

---

### Gold Layer

Data siap analitik.

Contoh:

```json
{
  "cve_id": "CVE-2026-12345",
  "priority_score": 96,
  "risk_level": "Critical"
}
```

Karakteristik:

* Analytics Ready
* Dashboard Ready
* Aggregated

---

## Vulnerability Prioritization Engine

ThreatLake menggunakan pendekatan rule-based scoring.

### Risk Factors

| Factor               | Weight |
| -------------------- | ------ |
| CVSS Score           | 40%    |
| KEV Status           | 30%    |
| Exploit Availability | 20%    |
| Advisory Activity    | 10%    |

### Risk Classification

| Score  | Level    |
| ------ | -------- |
| 90-100 | Critical |
| 70-89  | High     |
| 40-69  | Medium   |
| 0-39   | Low      |

---

## Dashboard Features

### Executive Dashboard

Menampilkan:

* Total CVE
* Critical CVE
* Exploited Vulnerabilities
* Vendor Risk Ranking
* Monthly Trend

### Analyst Dashboard

Menampilkan:

* CVE Search
* CVSS Distribution
* KEV Status
* Exploit Availability
* Advisory Timeline
* Vulnerability Ranking

---

## Technology Stack

| Layer                | Technology      |
| -------------------- | --------------- |
| Scheduler            | Apache Airflow  |
| Streaming            | Apache Kafka    |
| Processing           | Apache Spark    |
| Object Storage       | MinIO           |
| Lakehouse            | Apache Iceberg  |
| Query Engine         | Trino           |
| Dashboard            | Apache Superset |
| Deployment           | Docker Compose  |
| Programming Language | Python          |

---

## Project Structure

```text
threatlake/
│
├── docker/
│   ├── kafka/
│   ├── spark/
│   ├── trino/
│   ├── minio/
│   ├── superset/
│   └── airflow/
│
├── configs/
│   ├── kafka/
│   ├── spark/
│   ├── iceberg/
│   └── trino/
│
├── ingestion/
│   ├── nvd/
│   │   └── producer.py
│   │
│   ├── cisa/
│   │   └── producer.py
│   │
│   ├── github_advisory/
│   │   └── producer.py
│   │
│   ├── github_events/
│   │   └── producer.py
│   │
│   └── exploitdb/
│       └── producer.py
│
├── streaming/
│   ├── bronze_writer.py
│   ├── silver_processor.py
│   └── gold_processor.py
│
├── sql/
│   ├── bronze/
│   ├── silver/
│   └── gold/
│
├── airflow/
│   └── dags/
│
├── dashboards/
│
├── docs/
│
├── docker-compose.yml
│
└── README.md
```

---

## Expected Impact

ThreatLake membantu organisasi:

* Mempercepat proses vulnerability assessment.
* Mengurangi waktu analisis manual.
* Memusatkan threat intelligence dalam satu platform.
* Mendukung pengambilan keputusan berbasis data.
* Meningkatkan efektivitas patch management.

---

## Future Enhancements

* CVE Timeline Visualization
* Vendor Exposure Analytics
* Asset Correlation
* Threat Intelligence Feed Integration
* Real-Time Alerting via Discord/Slack/Email
* Multi-Organization Dashboard

```
```

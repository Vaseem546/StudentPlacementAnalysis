# Student Placement Analytics Platform

An enterprise-grade, end-to-end Data Engineering and Analytics Platform built with Python, PySpark, Snowflake, dbt (Core & Snowflake adapter), and Streamlit.

The platform processes student recruitment data across institutions, recruiters, academic branches, and compensation tiers. It implements Medallion Architecture (Bronze to Silver to Gold), Slowly Changing Dimensions Type 2 (SCD Type 2) tracking via dbt snapshots, Star Schema dimensional modeling, fine-grained Snowflake Role-Based Access Control (RBAC), dynamic data masking, row-level security, Snowpipe automated continuous ingestion via an internal stage, and a responsive executive Streamlit dashboard.

---

## Architecture Overview

```
                          +------------------------+
                          |   4 Source CSV Files   |
                          +-----------+------------+
                                      |
                                      v
                          +------------------------+
                          |    PySpark Pipeline    |
                          | (Clean & Profile Data) |
                          +-----------+------------+
                                      |
                                      v
                          +------------------------+
                          |     data/cleaned/      |
                          +-----------+------------+
                                      |
                                      v
+-----------------------------------------------------------------------------+
|                       SNOWFLAKE CLOUD DATA WAREHOUSE                        |
|                                                                             |
|  [INTERNAL STAGE - @STAGE_PLACEMENT]                                        |
|   CSV_INGEST_FORMAT | Dedicated partition folders per entity                |
|   Continuous ingestion triggered via ALTER PIPE <pipe_name> REFRESH         |
|                                     |                                       |
|                                     v                                       |
|  [BRONZE SCHEMA - RAW INGESTION]                                            |
|   RAW_STUDENTS  |  RAW_COLLEGES  |  RAW_COMPANIES  |  RAW_OFFERS            |
|   (Metadata: LOAD_TS, FILE_NAME, ROW_NUMBER, BATCH_ID)                      |
|                                     |                                       |
|                                     v (dbt Staging Views)                   |
|  [SILVER SCHEMA - STANDARDIZATION & CLEANING]                               |
|   STG_* Views   |  INT_*_CLEANED Tables                                     |
|   (Deduplication, NULL Handling, CGPA Bands, Domain Validation)             |
|                                     |                                       |
|                                     v (dbt Snapshots & Star Schema)         |
|  [GOLD SCHEMA - DIMENSIONAL STAR SCHEMA]                                    |
|   DIM_STUDENT (SCD2) | DIM_COMPANY (SCD2) | DIM_COLLEGE (Type 1)            |
|   DIM_DATE (Calendar)| FACT_PLACEMENT (Grain: Offer Line, Incremental Merge)|
|                                     |                                       |
|                                     v (dbt Analytical Marts)                |
|  [SEM SCHEMA - BUSINESS SEMANTIC VIEWS]                                     |
|   V_EXECUTIVE_SUMMARY | V_COLLEGE_PERFORMANCE                               |
|   V_COMPANY_INSIGHTS  | V_OFFER_EXPLORER                                    |
|                                                                             |
|  [OPS SCHEMA - AUDIT & TELEMETRY]                                           |
|   LOAD_AUDIT (Batch Logging) | REJECTS (Validation Failures)                |
+-------------------------------------+---------------------------------------+
                                      |
                                      v
                          +------------------------+
                          |  Streamlit Application |
                          | (Executive Analytics)  |
                          +------------------------+
```

---

## Technology Stack

| Layer | Technology | Version | Purpose |
| :--- | :--- | :--- | :--- |
| **Data Cleaning & Profiling** | PySpark / Python | Python 3.11, PySpark 3.5 | Raw schema inspection, data type validation, missingness profiling |
| **Cloud Data Warehouse** | Snowflake | Standard Edition | Relational storage, internal staging `@STAGE_PLACEMENT`, RBAC, Dynamic Masking, Row Access Policies |
| **Automated Ingestion** | Snowpipe | Serverless Pipes | Continuous auto-ingestion from internal stage via `ALTER PIPE ... REFRESH` |
| **In-Warehouse Transformations** | dbt (dbt-core, dbt-snowflake) | 1.12.4 / 1.12.0 | Medallion pipelines, SCD Type 2 snapshots, Star Schema facts/dimensions |
| **Data Quality & Testing** | dbt Generic Tests & Python | Custom suite | 76 automated dbt schema tests + 14 Python referential integrity checks |
| **Executive Intelligence** | Streamlit, Plotly | Streamlit 1.32, Plotly 6.x | Interactive business intelligence dashboard with 4 views and dynamic metrics |
| **Connectivity & Security** | snowflake-connector-python, python-dotenv | 3.13.0 | Parameterized connectivity, TLS encryption, credential isolation |

---

## Repository Structure

```text
StudentPlacementAnalysis/
├── .env                                # Snowflake credentials (git-ignored)
├── .gitignore                          # Protected environment and local exclusions
├── README.md                           # Comprehensive platform documentation
├── requirements.txt                    # Certified Python dependencies
│
├── .streamlit/
│   └── config.toml                     # Streamlit theme and browser auto-open config
│
├── data/                               # Source datasets and pipeline outputs
│   ├── placement_colleges.csv          # Raw colleges data (15 records)
│   ├── placement_companies.csv         # Raw companies data (15 records)
│   ├── placement_offers.csv            # Raw placement offers data (25 records)
│   ├── placement_students.csv          # Raw students data (20 records)
│   ├── student_placement_star_schema_diagram.png # Star Schema architectural entity diagram
│   └── cleaned/                        # PySpark cleaned output CSVs
│       ├── colleges.csv
│       ├── companies.csv
│       ├── offers.csv
│       └── students.csv
│
├── dbt_project/                        # Native dbt project root
│   ├── dbt_project.yml                 # Model materializations and layer configurations
│   ├── profiles.yml                    # Snowflake adapter connection profile
│   ├── macros/
│   │   └── generate_schema_name.sql    # Clean target schema resolver (SILVER, GOLD, SEM)
│   ├── snapshots/                      # Slowly Changing Dimensions Type 2
│   │   ├── snap_students.sql           # Tracks academic & location profile changes
│   │   └── snap_companies.sql          # Tracks recruiter size, industry & status changes
│   └── models/
│       ├── bronze/                     # Staging layer views (stg_placement_*.sql & sources.yml)
│       ├── silver/                     # Intermediate cleaned tables (int_*_cleaned.sql)
│       └── gold/                       # Analytical dimensional models
│           ├── dimensions/             # Dimension tables (DIM_STUDENT, DIM_COMPANY, DIM_COLLEGE, DIM_DATE)
│           ├── facts/                  # Fact table (FACT_PLACEMENT incremental merge)
│           └── marts/                  # Semantic analytical views (V_EXECUTIVE_SUMMARY, etc.)
│
├── sql/                                # Snowflake DDL scripts
│   ├── database_setup.sql              # Warehouse, Database, and Schema creation
│   ├── roles.sql                       # Enterprise RBAC role hierarchy and grants
│   ├── schemas.sql                     # Operational telemetry tables (LOAD_AUDIT, REJECTS)
│   ├── snowpipe_setup.sql              # Internal stage, CSV format, Bronze tables, and 4 Snowpipes
│   └── security.sql                    # Dynamic Data Masking and Row Access Policies
│
├── src/                                # Core Python source code (clean, concise, human-written)
│   ├── config.py                       # Environment variable loader
│   ├── snowflake_connection.py         # Standard connection factory
│   ├── ingestion/
│   │   └── load_bronze.py              # Snowpipe staging & loading with audit logging
│   ├── pyspark/
│   │   └── pipeline.py                 # PySpark data profiling, cleaning, and export
│   ├── snowflake/
│   │   └── setup_snowflake.py          # Database DDL initialization script
│   └── validation/
│       └── data_quality.py             # 14 automated data quality verification checks
│
├── streamlit/
│   └── app.py                          # 110-line executive Streamlit dashboard
│
└── tests/
    └── test_end_to_end.py              # 10-test automated verification suite
```

---

## Medallion Architecture Implementation

The platform organizes data across three logical tiers in Snowflake, ensuring data lineage, immutability, and analytical readiness:

### 1. Bronze Layer (`PLACEMENT_DB.BRONZE`)
* **Tables**: `RAW_STUDENTS`, `RAW_COLLEGES`, `RAW_COMPANIES`, `RAW_OFFERS`.
* **Nature**: Raw, immutable ingestion via Snowflake Snowpipe and internal stage `@STAGE_PLACEMENT`.
* **Metadata Injection**: Every ingested row is automatically enriched with operational telemetry:
  * `LOAD_TS`: Exact UTC timestamp of the ingestion event.
  * `FILE_NAME`: Source CSV file origin (`METADATA$FILENAME`).
  * `ROW_NUMBER`: File index sequence number (`METADATA$FILE_ROW_NUMBER`).
  * `BATCH_ID`: Unique batch identifier.

### 2. Silver Layer (`PLACEMENT_DB.SILVER`)
* **Staging Views (`models/bronze/`)**: `STG_PLACEMENT_STUDENTS`, `STG_PLACEMENT_COLLEGES`, `STG_PLACEMENT_COMPANIES`, `STG_PLACEMENT_OFFERS`.
  * Trims whitespace, standardizes casing, casts dates and numerics, applies standardized column aliases.
* **Cleaned Tables (`models/silver/`)**: `INT_STUDENTS_CLEANED`, `INT_COLLEGES_CLEANED`, `INT_COMPANIES_CLEANED`, `INT_OFFERS_CLEANED`.
  * Deduplication using window functions: `ROW_NUMBER() OVER (PARTITION BY <id> ORDER BY updated_at DESC)`.
  * Feature Engineering: Computed `CGPA_BAND` (`9+`, `8-9`, `7-8`, `6-7`, `<6`).
  * Domain Validation: Filters out non-positive compensation values (`ctc_lpa > 0`).
  * Referential Integrity: Inner joins to parent entities ensuring zero orphaned records.

### 3. Gold Layer (`PLACEMENT_DB.GOLD`) - Star Schema
* **Dimension: `DIM_STUDENT` (SCD Type 2)**:
  * Built from dbt snapshot `snap_students`.
  * Tracks historical revisions to student records: program, branch, graduation year, CGPA band, segment, and city.
  * Columns: `SK_STUDENT` (surrogate key), `STUDENT_ID`, `HASH_DIFF`, `EFF_START_TS`, `EFF_END_TS` (`9999-12-31` for active), `IS_CURRENT`.
* **Dimension: `DIM_COMPANY` (SCD Type 2)**:
  * Built from dbt snapshot `snap_companies`.
  * Tracks historical changes in recruiter size band, industry, hiring city, state, and partnership status.
  * Columns: `SK_COMPANY` (surrogate key), `COMPANY_ID`, `HASH_DIFF`, `EFF_START_TS`, `EFF_END_TS`, `IS_CURRENT`.
* **Dimension: `DIM_COLLEGE` (Type 1 Overwrite)**:
  * Contains college master attributes: `SK_COLLEGE`, `COLLEGE_ID`, `COLLEGE_NAME`, `CITY`, `STATE`, `TIER`, `CATEGORY`, `OWNERSHIP`.
* **Dimension: `DIM_DATE` (10-Year Calendar Spine)**:
  * Generated date spine spanning 3,653 days (2020-01-01 to 2029-12-31).
  * Columns: `SK_DATE` (`YYYYMMDD` integer), `DATE_VALUE`, `DAY_OF_WEEK`, `DAY_NAME`, `MONTH_NUM`, `MONTH_NAME`, `QUARTER`, `YEAR`, `IS_WEEKEND`.
* **Fact: `FACT_PLACEMENT`**:
  * Grain: Exactly one row per offer line `(OFFER_ID, OFFER_LINE_ID)`.
  * Incremental Materialization: Uses `incremental_strategy='merge'` on `(OFFER_ID, OFFER_LINE_ID)` with point-in-time surrogate key joins against SCD2 dimensions.
  * Metrics: `CTC_LPA`, `MONTHLY_STIPEND`, `IS_ACCEPTED`, `IS_JOINED`, `OFFER_LEVEL`, `OFFER_STATUS`.

### 4. Semantic Layer (`PLACEMENT_DB.SEM`)
* `V_EXECUTIVE_SUMMARY`: High-level aggregated KPIs (Total Offers, Placement Rate %, Acceptance Rate %, Average CTC, Median CTC).
* `V_COLLEGE_PERFORMANCE`: Institutional metrics, tier benchmarks, branch averages, and student counts.
* `V_COMPANY_INSIGHTS`: Recruiter hiring volume, industry breakdown, job city distribution, and average CTC.
* `V_OFFER_EXPLORER`: Denormalized offer-level grain view powering the interactive explorer and CSV export.

---

## Security, Governance & Compliance

### 1. Role-Based Access Control (RBAC)
The Snowflake security hierarchy enforces strict separation of concerns and least privilege:

```text
               ACCOUNTADMIN
                    │
                SYSADMIN
                    │
            ┌───────┴───────┐
            │               │
        ROLE_ETL       ROLE_ADMIN
            │
    ┌───────┴───────┐
    │               │
ROLE_INGEST    ROLE_ANALYST
                    │
          ROLE_APP_STREAMLIT (Least Privilege)
```

* `ROLE_INGEST`: Write access to `BRONZE` and `OPS.LOAD_AUDIT`.
* `ROLE_ETL`: Full transformation access across `BRONZE`, `SILVER`, `GOLD`, `OPS`, and `SEM`.
* `ROLE_ANALYST`: Read-only analytical querying on `SILVER`, `GOLD`, and `SEM`.
* `ROLE_APP_STREAMLIT`: Restricted strictly to `SELECT` privileges on the `SEM` schema. Direct access to raw data or operational tables is prohibited.

### 2. Dynamic Data Masking (PII Protection)
Protects student Personally Identifiable Information (PII) at query time without altering stored data:
* `BRONZE.MASK_NAME`: Student first and last names display as `***MASKED***` unless the querying role is `ROLE_ADMIN` or `ROLE_ETL`.
* `BRONZE.MASK_DOB`: Dates of birth display as `****-**-**` for unauthorized roles.

### 3. Row-Level Security (Row Access Policies)
* `GOLD.RAP_ACTIVE_COLLEGES`: Limits standard analyst queries to institutions with `STATUS = 'ACTIVE'`.
* `GOLD.RAP_ACTIVE_COMPANIES`: Limits recruiter visibility to active corporate partners.

### 4. Operations & Auditing (`PLACEMENT_DB.OPS`)
* `OPS.LOAD_AUDIT`: Central audit log tracking every ingestion, data quality check, and pipeline run with execution timestamps, row counts, batch IDs, and statuses.
* `OPS.REJECTS`: Captures rows rejected during validation along with failure reasons.

---

## Data Quality & Testing Framework

The platform includes a multi-layered verification system:

### 1. Automated dbt Tests (76 Tests)
* **Uniqueness**: Surrogate keys (`SK_STUDENT`, `SK_COMPANY`, `SK_COLLEGE`, `SK_DATE`, `SK_FACT_PLACEMENT`) and natural keys.
* **Not Null**: Primary identifiers, timestamps, compensation values, and foreign keys.
* **Accepted Values**: `OFFER_STATUS` (`OFFERED`, `ACCEPTED`, `JOINED`, `REJECTED`, `WITHDRAWN`), `OFFER_LEVEL` (`FTE`, `INTERN`), `IS_JOINED` (`0`, `1`).
* **Relationships (Referential Integrity)**: Foreign keys in `FACT_PLACEMENT` match surrogate keys in dimensions.

### 2. Automated Python Data Quality Checks (14 Checks)
Script [src/validation/data_quality.py](file:///c:/Users/Lenovo/Desktop/StudentPlacementAnalysis/src/validation/data_quality.py) executes and logs 14 automated assertions:
1. Duplicate student IDs in Bronze.
2. Duplicate college IDs in Bronze.
3. Duplicate company IDs in Bronze.
4. Duplicate offer identifiers in Bronze.
5. Null checks on critical student fields.
6. Domain bounds on CGPA (`0.0 <= CGPA <= 10.0`).
7. Domain bounds on compensation (`CTC_LPA > 0`).
8. Accepted offer status domain values.
9. Referential integrity: Orphaned student references.
10. Referential integrity: Orphaned college references.
11. Referential integrity: Orphaned company references.
12. Date order integrity: Expected join date not earlier than offer date.
13. Star schema referential integrity across all 4 dimension foreign keys.
14. SCD Type 2 temporal consistency: Current records active until `9999-12-31`.

### 3. End-to-End Test Suite (10 Tests)
Script [tests/test_end_to_end.py](file:///c:/Users/Lenovo/Desktop/StudentPlacementAnalysis/tests/test_end_to_end.py) verifies the entire operational pipeline with 10 unit test checkpoints. All tests pass with zero errors.

---

## Streamlit Executive Dashboard

The interactive dashboard ([streamlit/app.py](file:///c:/Users/Lenovo/Desktop/StudentPlacementAnalysis/streamlit/app.py)) is implemented in 110 lines of clean Python:

### Pages and Visualizations

1. **Executive Placement Overview**:
   - 6 Uniform KPI Cards:
     - Total Offers: `25` (12 Candidates)
     - Accepted Offers: `9` (36.0% Acceptance)
     - Joined Offers: `5` (55.56% Conversion)
     - Placement Rate: `41.67%` (Overall Cohort)
     - Average CTC: `26.2 LPA` (Range: 7.2 - 42.0 LPA)
     - Median CTC: `26.8 LPA` (13 Companies)
   - Offers by Status (Bar chart).
   - Average CTC by Offer Level (Bar chart).
   - Top Recruiters by Offer Count (Horizontal bar chart).
   - Offer Date Timeline (Line chart with markers).

2. **College Performance Benchmark**:
   - Placement Rate by College (Horizontal bar chart with percentage labels).
   - Offers by College Tier (Bar chart with average CTC).
   - Average CTC by Academic Branch (Bar chart).
   - Offers by Graduation Year (Bar chart).
   - Detailed institutional performance table.

3. **Company & Recruiter Insights**:
   - Offers by Industry Sector (Horizontal bar chart).
   - Top Job Cities by Hiring Volume (Bar chart).
   - Recruiter Performance Table with acceptance rates and average CTC.

4. **Offer Explorer**:
   - 8 Multi-Select Filter Controls: College, College Tier, Company, Industry, Program, Branch, Offer Status, Job City.
   - 4 Dynamic KPI Summary Metrics: Filtered Offers, Average CTC, Accepted Count, Joined Count.
   - Filterable, sortable offer-level data table.
   - One-Click CSV Export button (`placement_offers_filtered.csv`).

---

## Step-by-Step Installation and Execution Guide

### Prerequisites
* Python 3.10 or 3.11 installed
* Snowflake account with administrative permissions
* Git installed

### 1. Clone Repository and Install Dependencies
```bash
git clone https://github.com/Vaseem546/StudentPlacementAnalysis.git
cd StudentPlacementAnalysis

python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

pip install -r requirements.txt
```

### 2. Configure Snowflake Credentials
Create a `.env` file in the project root:
```ini
SNOWFLAKE_ACCOUNT=your_account_identifier
SNOWFLAKE_USER=your_username
SNOWFLAKE_PASSWORD=your_password
SNOWFLAKE_WAREHOUSE=PLACEMENT_WH
SNOWFLAKE_DATABASE=PLACEMENT_DB
SNOWFLAKE_ROLE=ROLE_ETL
```

### 3. Initialize Snowflake Warehouse, Database, Schemas & Snowpipes
```bash
python src/snowflake/setup_snowflake.py
```
*Creates warehouse `PLACEMENT_WH`, database `PLACEMENT_DB`, schemas `BRONZE`, `SILVER`, `GOLD`, `OPS`, `SEM`, tables `OPS.LOAD_AUDIT` and `OPS.REJECTS`, internal landing stage `STAGE_PLACEMENT`, and 4 dedicated Snowpipes (`PIPE_RAW_STUDENTS`, `PIPE_RAW_COLLEGES`, `PIPE_RAW_COMPANIES`, `PIPE_RAW_OFFERS`).*

### 4. Run PySpark Local Data Pipeline
```bash
python src/pyspark/pipeline.py
```
*Profiles and cleans raw CSVs, computing `CGPA_BAND` and saving validated outputs to `data/cleaned/`.*

### 5. Ingest Raw Data into Bronze via Snowpipe
```bash
python src/ingestion/load_bronze.py
```
*Stages the 4 source CSVs into internal stage `@STAGE_PLACEMENT` using `PUT`, triggers the 4 Snowpipes with `ALTER PIPE ... REFRESH`, and logs batch execution telemetry to `OPS.LOAD_AUDIT`.*

### 6. Execute Native dbt Pipeline
You can run dbt natively using either of the following:

#### Option A (From project root):
```bash
dbt run --project-dir dbt_project --profiles-dir dbt_project
dbt snapshot --project-dir dbt_project --profiles-dir dbt_project
dbt test --project-dir dbt_project --profiles-dir dbt_project
```

#### Option B (Inside dbt_project):
```bash
cd dbt_project
dbt run
dbt snapshot
dbt test
cd ..
```

### 7. Run Data Quality & End-to-End Tests
```bash
# Execute the 14 automated data quality checks
python src/validation/data_quality.py

# Run the 10-checkpoint end-to-end unit test suite
python -m unittest tests/test_end_to_end.py
```

### 8. Launch the Streamlit Dashboard
```bash
streamlit run streamlit/app.py
```
*Open `http://localhost:8501` in your browser.*

---

## Verification and Test Results

Execution of `python -m unittest tests/test_end_to_end.py`:

```text
Ran 10 tests in 9.181s

OK
```

All 76 dbt tests, 14 data quality checks, and 10 end-to-end integration tests execute with zero violations and 100% pass rates.

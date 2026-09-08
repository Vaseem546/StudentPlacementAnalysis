-- ============================================================
-- PHASE 4: DATABASE, WAREHOUSE, SCHEMAS
-- Run this in Snowflake as ACCOUNTADMIN or SYSADMIN
-- ============================================================

-- Warehouse
CREATE WAREHOUSE IF NOT EXISTS PLACEMENT_WH
    WAREHOUSE_SIZE = 'X-SMALL'
    AUTO_SUSPEND   = 60
    AUTO_RESUME    = TRUE
    COMMENT        = 'Placement Analytics Warehouse';

-- Database
CREATE DATABASE IF NOT EXISTS PLACEMENT_DB
    COMMENT = 'Student Placement Analytics Platform';

USE DATABASE PLACEMENT_DB;

-- Schemas
CREATE SCHEMA IF NOT EXISTS BRONZE  COMMENT = 'Raw ingested data';
CREATE SCHEMA IF NOT EXISTS SILVER  COMMENT = 'Cleaned and validated data';
CREATE SCHEMA IF NOT EXISTS GOLD    COMMENT = 'Star schema - dimensions and facts';
CREATE SCHEMA IF NOT EXISTS OPS     COMMENT = 'Audit, rejects and monitoring';
CREATE SCHEMA IF NOT EXISTS SEM     COMMENT = 'Semantic views for Streamlit';

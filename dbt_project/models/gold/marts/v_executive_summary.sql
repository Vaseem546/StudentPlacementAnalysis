{{ config(materialized='view', schema='SEM') }}

WITH base AS (
    SELECT
        f.offer_id,
        f.offer_line_id,
        f.student_id,
        f.company_id,
        f.college_id,
        f.ctc_lpa,
        f.monthly_stipend,
        f.offer_status,
        f.is_joined,
        f.is_accepted,
        f.offer_date
    FROM {{ ref('fact_placement') }} f
)

SELECT
    COUNT(*) AS total_offers,
    COUNT(DISTINCT student_id) AS total_candidates,
    COUNT(CASE WHEN is_accepted = 1 THEN 1 END) AS accepted_offers,
    COUNT(CASE WHEN is_joined = 1 THEN 1 END) AS joined_offers,
    ROUND(100.0 * COUNT(CASE WHEN is_accepted = 1 THEN 1 END) / NULLIF(COUNT(*), 0), 2) AS acceptance_rate_pct,
    ROUND(100.0 * COUNT(CASE WHEN is_joined = 1 THEN 1 END) / NULLIF(COUNT(DISTINCT student_id), 0), 2) AS placement_rate_pct,
    ROUND(100.0 * COUNT(CASE WHEN is_joined = 1 THEN 1 END) / NULLIF(COUNT(CASE WHEN is_accepted = 1 THEN 1 END), 0), 2) AS join_conversion_rate_pct,
    ROUND(AVG(ctc_lpa), 2) AS avg_ctc,
    ROUND(MEDIAN(ctc_lpa), 2) AS median_ctc,
    MIN(ctc_lpa) AS min_ctc,
    MAX(ctc_lpa) AS max_ctc,
    ROUND(AVG(monthly_stipend), 2) AS avg_monthly_stipend,
    COUNT(DISTINCT company_id) AS total_companies,
    COUNT(DISTINCT college_id) AS total_colleges
FROM base

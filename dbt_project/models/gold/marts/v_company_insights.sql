{{ config(materialized='view', schema='SEM') }}

WITH base AS (
    SELECT
        f.offer_id,
        f.student_id,
        f.ctc_lpa,
        f.monthly_stipend,
        f.role_title,
        f.offer_level,
        f.job_city,
        f.hiring_mode,
        f.offer_status,
        f.is_joined,
        f.is_accepted,
        c.company_id,
        c.company_name,
        c.industry,
        c.size_band,
        c.hiring_city AS company_hiring_city,
        c.hiring_state AS company_hiring_state
    FROM {{ ref('fact_placement') }} f
    JOIN {{ ref('dim_company') }} c ON f.sk_company = c.sk_company
)

SELECT
    company_id,
    company_name,
    industry,
    size_band,
    company_hiring_city,
    company_hiring_state,
    role_title,
    offer_level,
    hiring_mode,
    COUNT(*) AS total_offers,
    COUNT(CASE WHEN is_accepted = 1 THEN 1 END) AS accepted_offers,
    COUNT(CASE WHEN is_joined = 1 THEN 1 END) AS joined_offers,
    ROUND(100.0 * COUNT(CASE WHEN is_accepted = 1 THEN 1 END) / NULLIF(COUNT(*), 0), 2) AS acceptance_rate_pct,
    ROUND(100.0 * COUNT(CASE WHEN is_joined = 1 THEN 1 END) / NULLIF(COUNT(CASE WHEN is_accepted = 1 THEN 1 END), 0), 2) AS join_conversion_rate_pct,
    ROUND(AVG(ctc_lpa), 2) AS avg_ctc,
    ROUND(MEDIAN(ctc_lpa), 2) AS median_ctc,
    ROUND(AVG(monthly_stipend), 2) AS avg_monthly_stipend
FROM base
GROUP BY
    company_id,
    company_name,
    industry,
    size_band,
    company_hiring_city,
    company_hiring_state,
    role_title,
    offer_level,
    hiring_mode

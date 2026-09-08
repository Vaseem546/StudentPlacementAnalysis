{{ config(materialized='view', schema='SEM') }}

WITH base AS (
    SELECT
        f.offer_id,
        f.student_id,
        f.ctc_lpa,
        f.offer_status,
        f.is_joined,
        f.is_accepted,
        cl.college_id,
        cl.college_name,
        cl.tier AS college_tier,
        cl.category AS college_category,
        cl.ownership AS college_ownership,
        cl.city AS college_city,
        cl.state AS college_state,
        s.program,
        s.branch,
        s.grad_year,
        s.cgpa_band
    FROM {{ ref('fact_placement') }} f
    JOIN {{ ref('dim_college') }} cl ON f.sk_college = cl.sk_college
    JOIN {{ ref('dim_student') }} s ON f.sk_student = s.sk_student
)

SELECT
    college_id,
    college_name,
    college_tier,
    college_category,
    college_ownership,
    college_city,
    college_state,
    program,
    branch,
    grad_year,
    COUNT(*) AS total_offers,
    COUNT(DISTINCT student_id) AS student_count,
    COUNT(CASE WHEN is_accepted = 1 THEN 1 END) AS accepted_offers,
    COUNT(CASE WHEN is_joined = 1 THEN 1 END) AS joined_offers,
    ROUND(100.0 * COUNT(CASE WHEN is_joined = 1 THEN 1 END) / NULLIF(COUNT(DISTINCT student_id), 0), 2) AS placement_rate_pct,
    ROUND(AVG(ctc_lpa), 2) AS avg_ctc,
    ROUND(MEDIAN(ctc_lpa), 2) AS median_ctc,
    MIN(ctc_lpa) AS min_ctc,
    MAX(ctc_lpa) AS max_ctc
FROM base
GROUP BY
    college_id,
    college_name,
    college_tier,
    college_category,
    college_ownership,
    college_city,
    college_state,
    program,
    branch,
    grad_year

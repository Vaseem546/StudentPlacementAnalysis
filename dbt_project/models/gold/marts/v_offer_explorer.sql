{{ config(materialized='view', schema='SEM') }}

SELECT
    f.offer_id,
    f.offer_line_id,
    f.offer_date,
    f.expected_join_date,
    d.year AS offer_year,
    d.quarter AS offer_quarter,
    d.month AS offer_month,
    d.month_name AS offer_month_name,
    f.student_id,
    s.gender AS student_gender,
    s.program,
    s.branch,
    s.grad_year,
    s.cgpa,
    s.cgpa_band,
    s.city AS student_city,
    s.state AS student_state,
    s.segment AS student_segment,
    f.college_id,
    cl.college_name,
    cl.tier AS college_tier,
    cl.category AS college_category,
    cl.ownership AS college_ownership,
    cl.city AS college_city,
    cl.state AS college_state,
    f.company_id,
    c.company_name,
    c.industry,
    c.size_band,
    c.hiring_city AS company_hiring_city,
    f.role_title,
    f.offer_level,
    f.ctc_lpa,
    f.monthly_stipend,
    f.job_city,
    f.hiring_mode,
    f.offer_status,
    f.is_joined,
    f.is_accepted
FROM {{ ref('fact_placement') }} f
JOIN {{ ref('dim_student') }} s ON f.sk_student = s.sk_student
JOIN {{ ref('dim_company') }} c ON f.sk_company = c.sk_company
JOIN {{ ref('dim_college') }} cl ON f.sk_college = cl.sk_college
JOIN {{ ref('dim_date') }} d ON f.sk_offer_date = d.sk_date

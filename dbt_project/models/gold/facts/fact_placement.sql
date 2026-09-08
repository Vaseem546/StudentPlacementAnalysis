{{
    config(
        materialized='incremental',
        unique_key=['offer_id', 'offer_line_id'],
        incremental_strategy='merge'
    )
}}

WITH offers AS (
    SELECT * FROM {{ ref('int_offers_cleaned') }}
    {% if is_incremental() %}
        WHERE updated_at > (SELECT MAX(updated_at) FROM {{ this }})
           OR load_ts > (SELECT MAX(load_ts) FROM {{ this }})
    {% endif %}
),

students AS (
    SELECT * FROM {{ ref('dim_student') }}
),

companies AS (
    SELECT * FROM {{ ref('dim_company') }}
),

colleges AS (
    SELECT * FROM {{ ref('dim_college') }}
)

SELECT
    MD5(CONCAT_WS('||', o.offer_id, CAST(o.offer_line_id AS VARCHAR))) AS sk_fact_placement,
    o.offer_id,
    o.offer_line_id,
    CAST(TO_CHAR(o.offer_date, 'YYYYMMDD') AS INTEGER) AS sk_offer_date,
    CAST(TO_CHAR(o.expected_join_date, 'YYYYMMDD') AS INTEGER) AS sk_join_date,
    COALESCE(s.sk_student, s_curr.sk_student) AS sk_student,
    COALESCE(c.sk_company, c_curr.sk_company) AS sk_company,
    cl.sk_college,
    o.student_id,
    o.company_id,
    o.college_id,
    o.offer_date,
    o.expected_join_date,
    o.role_title,
    o.offer_level,
    o.ctc_lpa,
    o.monthly_stipend,
    o.job_city,
    o.hiring_mode,
    o.offer_status,
    o.is_joined,
    o.is_accepted,
    o.updated_at,
    o.load_ts,
    o.batch_id
FROM offers o
LEFT JOIN students s 
    ON o.student_id = s.student_id
   AND o.offer_date >= s.eff_start_ts::DATE
   AND o.offer_date < s.eff_end_ts::DATE
LEFT JOIN students s_curr
    ON o.student_id = s_curr.student_id
   AND s_curr.is_current = TRUE
LEFT JOIN companies c 
    ON o.company_id = c.company_id
   AND o.offer_date >= c.eff_start_ts::DATE
   AND o.offer_date < c.eff_end_ts::DATE
LEFT JOIN companies c_curr
    ON o.company_id = c_curr.company_id
   AND c_curr.is_current = TRUE
LEFT JOIN colleges cl
    ON o.college_id = cl.college_id

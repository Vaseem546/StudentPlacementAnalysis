WITH offers AS (
    SELECT * FROM {{ ref('stg_placement_offers') }}
),

students AS (
    SELECT student_id FROM {{ ref('int_students_cleaned') }}
),

colleges AS (
    SELECT college_id FROM {{ ref('int_colleges_cleaned') }}
),

companies AS (
    SELECT company_id FROM {{ ref('int_companies_cleaned') }}
),

validated AS (
    SELECT
        o.offer_id,
        o.offer_line_id,
        o.offer_date,
        o.expected_join_date,
        o.student_id,
        o.company_id,
        o.college_id,
        o.role_title,
        o.offer_level,
        o.ctc_lpa,
        o.monthly_stipend,
        o.job_city,
        o.hiring_mode,
        o.offer_status,
        CASE
            WHEN o.offer_status = 'JOINED' OR o.is_joined = 1 THEN 1
            ELSE 0
        END AS is_joined,
        CASE
            WHEN o.offer_status IN ('ACCEPTED', 'JOINED') THEN 1
            ELSE 0
        END AS is_accepted,
        o.updated_at,
        o.load_ts,
        o.batch_id,
        ROW_NUMBER() OVER (
            PARTITION BY o.offer_id, o.offer_line_id 
            ORDER BY o.updated_at DESC, o.load_ts DESC
        ) AS rn
    FROM offers o
    INNER JOIN students s ON o.student_id = s.student_id
    INNER JOIN colleges cl ON o.college_id = cl.college_id
    INNER JOIN companies co ON o.company_id = co.company_id
    WHERE o.offer_id IS NOT NULL
      AND o.offer_line_id IS NOT NULL
      AND o.ctc_lpa > 0
      AND o.offer_status IN ('OFFERED', 'ACCEPTED', 'JOINED', 'REJECTED', 'WITHDRAWN')
)

SELECT
    offer_id,
    offer_line_id,
    offer_date,
    expected_join_date,
    student_id,
    company_id,
    college_id,
    role_title,
    offer_level,
    ctc_lpa,
    monthly_stipend,
    job_city,
    hiring_mode,
    offer_status,
    is_joined,
    is_accepted,
    updated_at,
    load_ts,
    batch_id
FROM validated
WHERE rn = 1

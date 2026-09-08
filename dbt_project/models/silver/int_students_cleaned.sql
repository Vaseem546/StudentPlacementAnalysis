WITH source AS (
    SELECT * FROM {{ ref('stg_placement_students') }}
),

ranked AS (
    SELECT
        student_id,
        first_name,
        last_name,
        gender,
        dob,
        college_id,
        program,
        branch,
        grad_year,
        cgpa,
        CASE
            WHEN cgpa >= 9.0 THEN '9+ Excellent'
            WHEN cgpa >= 8.0 THEN '8-9 Very Good'
            WHEN cgpa >= 7.0 THEN '7-8 Good'
            ELSE '6-7 Average'
        END AS cgpa_band,
        city,
        state,
        country,
        segment,
        updated_at,
        load_ts,
        batch_id,
        ROW_NUMBER() OVER (
            PARTITION BY student_id 
            ORDER BY updated_at DESC, load_ts DESC
        ) AS rn
    FROM source
    WHERE student_id IS NOT NULL
      AND cgpa >= 0.0 AND cgpa <= 10.0
)

SELECT
    student_id,
    first_name,
    last_name,
    gender,
    dob,
    college_id,
    program,
    branch,
    grad_year,
    cgpa,
    cgpa_band,
    city,
    state,
    country,
    segment,
    updated_at,
    load_ts,
    batch_id
FROM ranked
WHERE rn = 1

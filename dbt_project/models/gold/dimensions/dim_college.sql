WITH source AS (
    SELECT * FROM {{ ref('int_colleges_cleaned') }}
)

SELECT
    MD5(college_id) AS sk_college,
    college_id,
    college_name,
    city,
    state,
    country,
    ownership,
    tier,
    category,
    established_date,
    status
FROM source

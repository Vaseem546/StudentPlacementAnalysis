WITH snapshot_data AS (
    SELECT * FROM {{ ref('snap_students') }}
)

SELECT
    MD5(CONCAT_WS('||', student_id, CAST(dbt_valid_from AS VARCHAR))) AS sk_student,
    student_id,
    first_name,
    last_name,
    gender,
    college_id,
    program,
    branch,
    grad_year,
    cgpa,
    cgpa_band,
    segment,
    city,
    state,
    country,
    MD5(CONCAT_WS('||', 
        COALESCE(program, ''), 
        COALESCE(branch, ''), 
        COALESCE(CAST(grad_year AS VARCHAR), ''), 
        COALESCE(cgpa_band, ''), 
        COALESCE(segment, ''), 
        COALESCE(city, ''), 
        COALESCE(state, '')
    )) AS hash_diff,
    dbt_valid_from AS eff_start_ts,
    COALESCE(dbt_valid_to, '9999-12-31 00:00:00'::TIMESTAMP_NTZ) AS eff_end_ts,
    CASE WHEN dbt_valid_to IS NULL THEN TRUE ELSE FALSE END AS is_current
FROM snapshot_data

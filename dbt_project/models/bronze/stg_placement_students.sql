WITH source AS (
    SELECT * FROM {{ source('bronze', 'RAW_STUDENTS') }}
),

renamed AS (
    SELECT
        TRIM(STUDENT_ID) AS student_id,
        TRIM(FIRST_NAME) AS first_name,
        TRIM(LAST_NAME) AS last_name,
        UPPER(TRIM(GENDER)) AS gender,
        TRY_TO_DATE(DOB) AS dob,
        TRIM(COLLEGE_ID) AS college_id,
        TRIM(PROGRAM) AS program,
        TRIM(BRANCH) AS branch,
        CAST(GRAD_YEAR AS INTEGER) AS grad_year,
        CAST(CGPA AS NUMBER(4,2)) AS cgpa,
        TRIM(CITY) AS city,
        UPPER(TRIM(STATE)) AS state,
        TRIM(COUNTRY) AS country,
        UPPER(TRIM(SEGMENT)) AS segment,
        TRY_TO_TIMESTAMP_NTZ(UPDATED_AT) AS updated_at,
        LOAD_TS AS load_ts,
        FILE_NAME AS file_name,
        BATCH_ID AS batch_id
    FROM source
)

SELECT * FROM renamed

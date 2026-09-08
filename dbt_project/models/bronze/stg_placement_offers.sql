WITH source AS (
    SELECT * FROM {{ source('bronze', 'RAW_OFFERS') }}
),

renamed AS (
    SELECT
        TRIM(OFFER_ID) AS offer_id,
        CAST(OFFER_LINE_ID AS INTEGER) AS offer_line_id,
        TRY_TO_DATE(OFFER_DATE) AS offer_date,
        TRY_TO_DATE(EXPECTED_JOIN_DATE) AS expected_join_date,
        TRIM(STUDENT_ID) AS student_id,
        TRIM(COMPANY_ID) AS company_id,
        TRIM(COLLEGE_ID) AS college_id,
        TRIM(ROLE_TITLE) AS role_title,
        UPPER(TRIM(OFFER_LEVEL)) AS offer_level,
        CAST(CTC_LPA AS NUMBER(6,2)) AS ctc_lpa,
        CAST(MONTHLY_STIPEND AS NUMBER(10,2)) AS monthly_stipend,
        TRIM(JOB_CITY) AS job_city,
        UPPER(TRIM(HIRING_MODE)) AS hiring_mode,
        UPPER(TRIM(OFFER_STATUS)) AS offer_status,
        CAST(IS_JOINED AS INTEGER) AS is_joined,
        TRY_TO_TIMESTAMP_NTZ(UPDATED_AT) AS updated_at,
        LOAD_TS AS load_ts,
        FILE_NAME AS file_name,
        BATCH_ID AS batch_id
    FROM source
)

SELECT * FROM renamed

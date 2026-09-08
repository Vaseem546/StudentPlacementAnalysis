WITH source AS (
    SELECT * FROM {{ source('bronze', 'RAW_COLLEGES') }}
),

renamed AS (
    SELECT
        TRIM(COLLEGE_ID) AS college_id,
        TRIM(COLLEGE_NAME) AS college_name,
        TRIM(CITY) AS city,
        UPPER(TRIM(STATE)) AS state,
        TRIM(COUNTRY) AS country,
        TRIM(OWNERSHIP) AS ownership,
        TRIM(TIER) AS tier,
        TRIM(CATEGORY) AS category,
        TRY_TO_DATE(ESTABLISHED_DATE) AS established_date,
        UPPER(TRIM(STATUS)) AS status,
        LOAD_TS AS load_ts,
        FILE_NAME AS file_name,
        BATCH_ID AS batch_id
    FROM source
)

SELECT * FROM renamed

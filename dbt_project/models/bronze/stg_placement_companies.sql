WITH source AS (
    SELECT * FROM {{ source('bronze', 'RAW_COMPANIES') }}
),

renamed AS (
    SELECT
        TRIM(COMPANY_ID) AS company_id,
        TRIM(COMPANY_NAME) AS company_name,
        TRIM(INDUSTRY) AS industry,
        TRIM(HQ_COUNTRY) AS hq_country,
        TRIM(SIZE_BAND) AS size_band,
        TRIM(HIRING_CITY) AS hiring_city,
        UPPER(TRIM(HIRING_STATE)) AS hiring_state,
        UPPER(TRIM(STATUS)) AS status,
        TRY_TO_DATE(PARTNER_SINCE) AS partner_since,
        TRY_TO_TIMESTAMP_NTZ(UPDATED_AT) AS updated_at,
        LOAD_TS AS load_ts,
        FILE_NAME AS file_name,
        BATCH_ID AS batch_id
    FROM source
)

SELECT * FROM renamed

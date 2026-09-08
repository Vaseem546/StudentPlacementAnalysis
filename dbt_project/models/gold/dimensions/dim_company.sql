WITH snapshot_data AS (
    SELECT * FROM {{ ref('snap_companies') }}
)

SELECT
    MD5(CONCAT_WS('||', company_id, CAST(dbt_valid_from AS VARCHAR))) AS sk_company,
    company_id,
    company_name,
    industry,
    hq_country,
    size_band,
    hiring_city,
    hiring_state,
    status,
    partner_since,
    MD5(CONCAT_WS('||',
        COALESCE(industry, ''),
        COALESCE(size_band, ''),
        COALESCE(hiring_city, ''),
        COALESCE(hiring_state, ''),
        COALESCE(status, '')
    )) AS hash_diff,
    dbt_valid_from AS eff_start_ts,
    COALESCE(dbt_valid_to, '9999-12-31 00:00:00'::TIMESTAMP_NTZ) AS eff_end_ts,
    CASE WHEN dbt_valid_to IS NULL THEN TRUE ELSE FALSE END AS is_current
FROM snapshot_data

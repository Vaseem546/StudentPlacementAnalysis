WITH source AS (
    SELECT * FROM {{ ref('stg_placement_companies') }}
),

ranked AS (
    SELECT
        company_id,
        company_name,
        COALESCE(industry, 'Other') AS industry,
        COALESCE(hq_country, 'India') AS hq_country,
        COALESCE(size_band, 'Medium') AS size_band,
        hiring_city,
        hiring_state,
        COALESCE(status, 'ACTIVE') AS status,
        partner_since,
        updated_at,
        load_ts,
        batch_id,
        ROW_NUMBER() OVER (
            PARTITION BY company_id 
            ORDER BY updated_at DESC, load_ts DESC
        ) AS rn
    FROM source
    WHERE company_id IS NOT NULL
)

SELECT
    company_id,
    company_name,
    industry,
    hq_country,
    size_band,
    hiring_city,
    hiring_state,
    status,
    partner_since,
    updated_at,
    load_ts,
    batch_id
FROM ranked
WHERE rn = 1

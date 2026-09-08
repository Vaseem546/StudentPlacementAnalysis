WITH source AS (
    SELECT * FROM {{ ref('stg_placement_colleges') }}
),

ranked AS (
    SELECT
        college_id,
        college_name,
        city,
        state,
        country,
        COALESCE(ownership, 'Unknown') AS ownership,
        COALESCE(tier, 'Tier-3') AS tier,
        COALESCE(category, 'General') AS category,
        established_date,
        COALESCE(status, 'ACTIVE') AS status,
        load_ts,
        batch_id,
        ROW_NUMBER() OVER (
            PARTITION BY college_id 
            ORDER BY load_ts DESC
        ) AS rn
    FROM source
    WHERE college_id IS NOT NULL
)

SELECT
    college_id,
    college_name,
    city,
    state,
    country,
    ownership,
    tier,
    category,
    established_date,
    status,
    load_ts,
    batch_id
FROM ranked
WHERE rn = 1

{% snapshot snap_companies %}

{{
    config(
      target_database='PLACEMENT_DB',
      target_schema='GOLD',
      unique_key='company_id',
      strategy='check',
      check_cols=['industry', 'size_band', 'hiring_city', 'hiring_state', 'status'],
      invalidate_hard_deletes=False
    )
}}

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
    updated_at
FROM {{ ref('int_companies_cleaned') }}

{% endsnapshot %}

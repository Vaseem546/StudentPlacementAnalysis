{% snapshot snap_students %}

{{
    config(
      target_database='PLACEMENT_DB',
      target_schema='GOLD',
      unique_key='student_id',
      strategy='check',
      check_cols=['program', 'branch', 'grad_year', 'cgpa_band', 'segment', 'city', 'state'],
      invalidate_hard_deletes=False
    )
}}

SELECT
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
    updated_at
FROM {{ ref('int_students_cleaned') }}

{% endsnapshot %}

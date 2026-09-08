WITH date_spine AS (
    SELECT
        DATEADD(DAY, SEQ4(), '2020-01-01'::DATE) AS date_value
    FROM TABLE(GENERATOR(ROWCOUNT => 3653))
)

SELECT
    CAST(TO_CHAR(date_value, 'YYYYMMDD') AS INTEGER) AS sk_date,
    date_value,
    EXTRACT(YEAR FROM date_value) AS year,
    EXTRACT(QUARTER FROM date_value) AS quarter,
    EXTRACT(MONTH FROM date_value) AS month,
    MONTHNAME(date_value) AS month_name,
    EXTRACT(WEEK FROM date_value) AS week_of_year,
    DAYNAME(date_value) AS day_of_week,
    CASE WHEN DAYNAME(date_value) IN ('Sat', 'Sun') THEN TRUE ELSE FALSE END AS is_weekend
FROM date_spine

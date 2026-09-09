use database PLACEMENT_DB;
use schema BRONZE;

create or replace file format PLACEMENT_DB.BRONZE.CSV_INGEST_FORMAT
    type = 'CSV'
    skip_header = 1
    field_optionally_enclosed_by = '"'
    null_if = ('', 'NULL', 'null')
    trim_space = true
    error_on_column_count_mismatch = false;

create or replace stage PLACEMENT_DB.BRONZE.STAGE_PLACEMENT
    file_format = PLACEMENT_DB.BRONZE.CSV_INGEST_FORMAT;

create table if not exists PLACEMENT_DB.BRONZE.RAW_STUDENTS (
    student_id varchar(100),
    first_name varchar(100),
    last_name varchar(100),
    gender varchar(10),
    dob varchar(50),
    college_id varchar(100),
    program varchar(100),
    branch varchar(100),
    grad_year number(38,0),
    cgpa float,
    city varchar(100),
    state varchar(100),
    country varchar(100),
    segment varchar(50),
    updated_at varchar(100),
    load_ts timestamp_ntz default current_timestamp(),
    file_name varchar(255),
    row_number number(38,0),
    batch_id varchar(100)
);

create table if not exists PLACEMENT_DB.BRONZE.RAW_COLLEGES (
    college_id varchar(100),
    college_name varchar(255),
    city varchar(100),
    state varchar(100),
    country varchar(100),
    ownership varchar(50),
    tier varchar(50),
    category varchar(100),
    established_date varchar(50),
    status varchar(50),
    load_ts timestamp_ntz default current_timestamp(),
    file_name varchar(255),
    row_number number(38,0),
    batch_id varchar(100)
);

create table if not exists PLACEMENT_DB.BRONZE.RAW_COMPANIES (
    company_id varchar(100),
    company_name varchar(255),
    industry varchar(100),
    hq_country varchar(100),
    size_band varchar(50),
    hiring_city varchar(100),
    hiring_state varchar(100),
    status varchar(50),
    partner_since varchar(50),
    updated_at varchar(100),
    load_ts timestamp_ntz default current_timestamp(),
    file_name varchar(255),
    row_number number(38,0),
    batch_id varchar(100)
);

create table if not exists PLACEMENT_DB.BRONZE.RAW_OFFERS (
    offer_id varchar(100),
    offer_line_id number(38,0),
    offer_date varchar(50),
    expected_join_date varchar(50),
    student_id varchar(100),
    company_id varchar(100),
    college_id varchar(100),
    role_title varchar(150),
    offer_level varchar(50),
    ctc_lpa float,
    monthly_stipend float,
    job_city varchar(100),
    hiring_mode varchar(50),
    offer_status varchar(50),
    is_joined number(38,0),
    updated_at varchar(100),
    load_ts timestamp_ntz default current_timestamp(),
    file_name varchar(255),
    row_number number(38,0),
    batch_id varchar(100)
);

create or replace pipe PLACEMENT_DB.BRONZE.PIPE_RAW_STUDENTS as
copy into PLACEMENT_DB.BRONZE.RAW_STUDENTS (
    student_id, first_name, last_name, gender, dob, college_id, program, branch, 
    grad_year, cgpa, city, state, country, segment, updated_at,
    load_ts, file_name, row_number, batch_id
) from (
    select $1, $2, $3, $4, $5, $6, $7, $8, 
           try_to_number($9), try_to_double($10), $11, $12, $13, $14, $15,
           current_timestamp(), metadata$filename, metadata$file_row_number, 'BATCH_INGEST'
    from @PLACEMENT_DB.BRONZE.STAGE_PLACEMENT/students/
) file_format = PLACEMENT_DB.BRONZE.CSV_INGEST_FORMAT on_error = 'CONTINUE';

create or replace pipe PLACEMENT_DB.BRONZE.PIPE_RAW_COLLEGES as
copy into PLACEMENT_DB.BRONZE.RAW_COLLEGES (
    college_id, college_name, city, state, country, ownership, tier, category, 
    established_date, status,
    load_ts, file_name, row_number, batch_id
) from (
    select $1, $2, $3, $4, $5, $6, $7, $8, $9, $10,
           current_timestamp(), metadata$filename, metadata$file_row_number, 'BATCH_INGEST'
    from @PLACEMENT_DB.BRONZE.STAGE_PLACEMENT/colleges/
) file_format = PLACEMENT_DB.BRONZE.CSV_INGEST_FORMAT on_error = 'CONTINUE';

create or replace pipe PLACEMENT_DB.BRONZE.PIPE_RAW_COMPANIES as
copy into PLACEMENT_DB.BRONZE.RAW_COMPANIES (
    company_id, company_name, industry, hq_country, size_band, hiring_city, hiring_state, 
    status, partner_since, updated_at,
    load_ts, file_name, row_number, batch_id
) from (
    select $1, $2, $3, $4, $5, $6, $7, $8, $9, $10,
           current_timestamp(), metadata$filename, metadata$file_row_number, 'BATCH_INGEST'
    from @PLACEMENT_DB.BRONZE.STAGE_PLACEMENT/companies/
) file_format = PLACEMENT_DB.BRONZE.CSV_INGEST_FORMAT on_error = 'CONTINUE';

create or replace pipe PLACEMENT_DB.BRONZE.PIPE_RAW_OFFERS as
copy into PLACEMENT_DB.BRONZE.RAW_OFFERS (
    offer_id, offer_line_id, offer_date, expected_join_date, student_id, company_id, college_id, 
    role_title, offer_level, ctc_lpa, monthly_stipend, job_city, hiring_mode, offer_status, 
    is_joined, updated_at,
    load_ts, file_name, row_number, batch_id
) from (
    select $1, try_to_number($2), $3, $4, $5, $6, $7, 
           $8, $9, try_to_double($10), try_to_double($11), $12, $13, $14, 
           try_to_number($15), $16,
           current_timestamp(), metadata$filename, metadata$file_row_number, 'BATCH_INGEST'
    from @PLACEMENT_DB.BRONZE.STAGE_PLACEMENT/offers/
) file_format = PLACEMENT_DB.BRONZE.CSV_INGEST_FORMAT on_error = 'CONTINUE';

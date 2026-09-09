use database PLACEMENT_DB;
use schema OPS;

create table if not exists OPS.LOAD_AUDIT (
    audit_id number autoincrement primary key,
    batch_id varchar(50),
    file_name varchar(200),
    entity varchar(50),
    load_ts timestamp_ntz default current_timestamp(),
    row_count number,
    status varchar(20),
    error_msg varchar(2000)
);

create table if not exists OPS.REJECTS (
    reject_id number autoincrement primary key,
    batch_id varchar(50),
    entity varchar(50),
    source_row variant,
    reject_reason varchar(500),
    rejected_at timestamp_ntz default current_timestamp()
);

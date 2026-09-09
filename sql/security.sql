use database PLACEMENT_DB;
use schema BRONZE;

create or replace masking policy BRONZE.MASK_NAME as (val string)
returns string ->
    case
        when current_role() in ('ROLE_ETL', 'ROLE_ADMIN', 'SYSADMIN') then val
        else '***MASKED***'
    end;

create or replace masking policy BRONZE.MASK_DOB as (val string)
returns string ->
    case
        when current_role() in ('ROLE_ETL', 'ROLE_ADMIN', 'SYSADMIN') then val
        else '****-**-**'
    end;

use schema GOLD;

create or replace row access policy GOLD.RAP_ACTIVE_COLLEGES
as (status string) returns boolean ->
    case
        when current_role() in ('ROLE_ADMIN', 'ROLE_ETL', 'SYSADMIN') then true
        else status = 'ACTIVE'
    end;

create or replace row access policy GOLD.RAP_ACTIVE_COMPANIES
as (status string) returns boolean ->
    case
        when current_role() in ('ROLE_ADMIN', 'ROLE_ETL', 'SYSADMIN', 'ACCOUNTADMIN') then true
        else status = 'ACTIVE'
    end;

alter table BRONZE.RAW_STUDENTS modify column FIRST_NAME set masking policy BRONZE.MASK_NAME;
alter table BRONZE.RAW_STUDENTS modify column LAST_NAME set masking policy BRONZE.MASK_NAME;
alter table BRONZE.RAW_STUDENTS modify column DOB set masking policy BRONZE.MASK_DOB;

alter table GOLD.DIM_COLLEGE add row access policy GOLD.RAP_ACTIVE_COLLEGES on (status);
alter table GOLD.DIM_COMPANY add row access policy GOLD.RAP_ACTIVE_COMPANIES on (status);

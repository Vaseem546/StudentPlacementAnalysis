use database PLACEMENT_DB;
use role ACCOUNTADMIN;

create role if not exists ROLE_ADMIN;
create role if not exists ROLE_INGEST;
create role if not exists ROLE_ETL;
create role if not exists ROLE_ANALYST;
create role if not exists ROLE_APP_STREAMLIT;

grant role ROLE_INGEST to role ROLE_ETL;
grant role ROLE_ETL to role ROLE_ADMIN;
grant role ROLE_ANALYST to role ROLE_ADMIN;
grant role ROLE_APP_STREAMLIT to role ROLE_ANALYST;
grant role ROLE_ADMIN to role SYSADMIN;

grant role ROLE_ADMIN to user VASEEM;
grant role ROLE_ETL to user VASEEM;
grant role ROLE_INGEST to user VASEEM;
grant role ROLE_ANALYST to user VASEEM;
grant role ROLE_APP_STREAMLIT to user VASEEM;

grant usage on warehouse PLACEMENT_WH to role ROLE_INGEST;
grant usage on warehouse PLACEMENT_WH to role ROLE_ETL;
grant usage on warehouse PLACEMENT_WH to role ROLE_ANALYST;
grant usage on warehouse PLACEMENT_WH to role ROLE_APP_STREAMLIT;

grant usage on database PLACEMENT_DB to role ROLE_INGEST;
grant usage on database PLACEMENT_DB to role ROLE_ETL;
grant usage on database PLACEMENT_DB to role ROLE_ANALYST;
grant usage on database PLACEMENT_DB to role ROLE_APP_STREAMLIT;

grant all privileges on schema PLACEMENT_DB.BRONZE to role ROLE_INGEST;
grant all privileges on schema PLACEMENT_DB.OPS to role ROLE_INGEST;

grant all privileges on schema PLACEMENT_DB.BRONZE to role ROLE_ETL;
grant all privileges on schema PLACEMENT_DB.SILVER to role ROLE_ETL;
grant all privileges on schema PLACEMENT_DB.GOLD to role ROLE_ETL;
grant all privileges on schema PLACEMENT_DB.OPS to role ROLE_ETL;
grant all privileges on schema PLACEMENT_DB.SEM to role ROLE_ETL;

grant usage on schema PLACEMENT_DB.SILVER to role ROLE_ANALYST;
grant usage on schema PLACEMENT_DB.GOLD to role ROLE_ANALYST;
grant usage on schema PLACEMENT_DB.SEM to role ROLE_ANALYST;
grant select on all tables in schema PLACEMENT_DB.SILVER to role ROLE_ANALYST;
grant select on all tables in schema PLACEMENT_DB.GOLD to role ROLE_ANALYST;
grant select on all views in schema PLACEMENT_DB.SEM to role ROLE_ANALYST;

grant usage on schema PLACEMENT_DB.SEM to role ROLE_APP_STREAMLIT;
grant select on all views in schema PLACEMENT_DB.SEM to role ROLE_APP_STREAMLIT;

grant select on future tables in schema PLACEMENT_DB.BRONZE to role ROLE_ETL;
grant select on future tables in schema PLACEMENT_DB.SILVER to role ROLE_ANALYST;
grant select on future tables in schema PLACEMENT_DB.GOLD to role ROLE_ANALYST;
grant select on future views in schema PLACEMENT_DB.SEM to role ROLE_ANALYST;
grant select on future views in schema PLACEMENT_DB.SEM to role ROLE_APP_STREAMLIT;

create warehouse if not exists PLACEMENT_WH
    warehouse_size = 'X-SMALL'
    auto_suspend = 60
    auto_resume = true;

create database if not exists PLACEMENT_DB;

use database PLACEMENT_DB;

create schema if not exists BRONZE;
create schema if not exists SILVER;
create schema if not exists GOLD;
create schema if not exists OPS;
create schema if not exists SEM;

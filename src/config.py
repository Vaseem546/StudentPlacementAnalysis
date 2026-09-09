import os
from dotenv import load_dotenv

load_dotenv()

SNOWFLAKE_CONFIG = {
    "account":   os.getenv("SNOWFLAKE_ACCOUNT"),
    "user":      os.getenv("SNOWFLAKE_USER"),
    "password":  os.getenv("SNOWFLAKE_PASSWORD"),
    "warehouse": os.getenv("SNOWFLAKE_WAREHOUSE", "PLACEMENT_WH"),
    "database":  os.getenv("SNOWFLAKE_DATABASE", "PLACEMENT_DB"),
    "schema":    os.getenv("SNOWFLAKE_SCHEMA", "BRONZE"),
    "role":      os.getenv("SNOWFLAKE_ROLE", "ROLE_ETL"),
}

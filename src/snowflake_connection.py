import snowflake.connector
from src.config import SNOWFLAKE_CONFIG


def get_connection():
    try:
        kwargs = {
            "account": SNOWFLAKE_CONFIG["account"],
            "user": SNOWFLAKE_CONFIG["user"],
            "password": SNOWFLAKE_CONFIG["password"],
            "warehouse": SNOWFLAKE_CONFIG["warehouse"],
            "database": SNOWFLAKE_CONFIG["database"],
            "schema": SNOWFLAKE_CONFIG["schema"],
        }
        if SNOWFLAKE_CONFIG.get("role"):
            kwargs["role"] = SNOWFLAKE_CONFIG["role"]
        return snowflake.connector.connect(**kwargs)
    except Exception as e:
        if "Role" in str(e) or "role" in str(e):
            kwargs.pop("role", None)
            return snowflake.connector.connect(**kwargs)
        raise e


def run_query(sql: str, conn=None):
    close_after = conn is None
    if conn is None:
        conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(sql)
        return cur.fetchall()
    finally:
        if close_after:
            conn.close()

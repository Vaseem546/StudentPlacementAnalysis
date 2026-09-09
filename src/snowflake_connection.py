import os
import snowflake.connector
from src.config import SNOWFLAKE_CONFIG

def get_connection():
    kwargs = {k: v for k, v in SNOWFLAKE_CONFIG.items() if v}
    try:
        return snowflake.connector.connect(**kwargs)
    except Exception:
        kwargs.pop("role", None)
        return snowflake.connector.connect(**kwargs)

def run_query(sql, conn=None):
    close = False
    if not conn:
        conn = get_connection()
        close = True
    cur = conn.cursor()
    try:
        cur.execute(sql)
        return cur.fetchall()
    finally:
        cur.close()
        if close:
            conn.close()

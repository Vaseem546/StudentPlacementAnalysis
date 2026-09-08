import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

import snowflake.connector
from dotenv import load_dotenv

load_dotenv()

SQL_FILES = [
    "sql/database_setup.sql",
    "sql/roles.sql",
    "sql/schemas.sql",
    "sql/security.sql",
]


def get_conn():
    try:
        return snowflake.connector.connect(
            account=os.getenv("SNOWFLAKE_ACCOUNT"),
            user=os.getenv("SNOWFLAKE_USER"),
            password=os.getenv("SNOWFLAKE_PASSWORD"),
            role="ACCOUNTADMIN",
            warehouse=os.getenv("SNOWFLAKE_WAREHOUSE", "PLACEMENT_WH"),
        )
    except Exception:
        return snowflake.connector.connect(
            account=os.getenv("SNOWFLAKE_ACCOUNT"),
            user=os.getenv("SNOWFLAKE_USER"),
            password=os.getenv("SNOWFLAKE_PASSWORD"),
            warehouse=os.getenv("SNOWFLAKE_WAREHOUSE", "PLACEMENT_WH"),
        )


def run_sql_file(cur, path):
    with open(path, "r") as f:
        sql = f.read()

    statements = [s.strip() for s in sql.split(";") if s.strip() and not s.strip().startswith("--")]
    ok = 0
    for stmt in statements:
        try:
            cur.execute(stmt)
            ok += 1
        except Exception as e:
            print(f"  [WARN on statement: {stmt[:60]}...] -> {e}")
    print(f"  [{path}] {ok}/{len(statements)} statements executed")


def main():
    print("Connecting to Snowflake...")
    conn = get_conn()
    cur = conn.cursor()

    for sql_file in SQL_FILES:
        print(f"\nRunning {sql_file} ...")
        run_sql_file(cur, sql_file)

    cur.close()
    conn.close()
    print("\nPhase 4 setup complete.")


if __name__ == "__main__":
    main()

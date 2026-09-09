import os
from dotenv import load_dotenv
import snowflake.connector

load_dotenv()

sql_files = [
    "sql/database_setup.sql",
    "sql/roles.sql",
    "sql/schemas.sql",
    "sql/snowpipe_setup.sql",
    "sql/security.sql",
]

def main():
    conn = snowflake.connector.connect(
        account=os.getenv("SNOWFLAKE_ACCOUNT"),
        user=os.getenv("SNOWFLAKE_USER"),
        password=os.getenv("SNOWFLAKE_PASSWORD"),
        warehouse=os.getenv("SNOWFLAKE_WAREHOUSE", "PLACEMENT_WH"),
    )
    cur = conn.cursor()

    for file_path in sql_files:
        print("Running", file_path)
        with open(file_path, "r") as f:
            lines = [line for line in f if not line.strip().startswith("--")]
            commands = "".join(lines).split(";")
            for cmd in commands:
                stmt = cmd.strip()
                if stmt:
                    try:
                        cur.execute(stmt)
                    except Exception as e:
                        print("Error running statement:", e)

    cur.close()
    conn.close()
    print("Snowflake setup done.")

if __name__ == "__main__":
    main()

import os
import sys
import time

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from src.snowflake_connection import get_connection

tables = [
    ("RAW_STUDENTS", "data/placement_students.csv", "students", "PIPE_RAW_STUDENTS", 20),
    ("RAW_COLLEGES", "data/placement_colleges.csv", "colleges", "PIPE_RAW_COLLEGES", 15),
    ("RAW_COMPANIES", "data/placement_companies.csv", "companies", "PIPE_RAW_COMPANIES", 15),
    ("RAW_OFFERS", "data/placement_offers.csv", "offers", "PIPE_RAW_OFFERS", 25),
]

def main():
    batch_id = f"batch_{int(time.time())}"
    conn = get_connection()
    cur = conn.cursor()

    for table, file_path, folder, pipe, expected in tables:
        cur.execute(f"truncate table PLACEMENT_DB.BRONZE.{table}")
        full_path = os.path.abspath(file_path).replace("\\", "/")
        cur.execute(f"put file://{full_path} @PLACEMENT_DB.BRONZE.STAGE_PLACEMENT/{folder}/{batch_id}/ auto_compress=true")
        cur.execute(f"alter pipe PLACEMENT_DB.BRONZE.{pipe} refresh")

    # wait for snowpipe to load
    for _ in range(10):
        time.sleep(2)
        cur.execute("select count(*) from PLACEMENT_DB.BRONZE.RAW_OFFERS")
        if cur.fetchone()[0] >= 25:
            break

    for table, file_path, folder, pipe, expected in tables:
        cur.execute(f"select count(*) from PLACEMENT_DB.BRONZE.{table}")
        cnt = cur.fetchone()[0]
        status = "SUCCESS" if cnt == expected else "PARTIAL"
        file_name = os.path.basename(file_path)
        cur.execute(
            "insert into PLACEMENT_DB.OPS.LOAD_AUDIT (batch_id, file_name, entity, load_ts, row_count, status) values (%s, %s, %s, current_timestamp(), %s, %s)",
            (batch_id, file_name, table, cnt, status)
        )
        print(f"{table}: {cnt}/{expected} rows loaded")

    cur.close()
    conn.close()

if __name__ == "__main__":
    main()

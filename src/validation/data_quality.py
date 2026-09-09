import sys
import os
import json
import time

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from src.snowflake_connection import get_connection

checks = [
    ("Check 1: Duplicate Student IDs", "RAW_STUDENTS", "select student_id from PLACEMENT_DB.BRONZE.RAW_STUDENTS group by student_id having count(*) > 1", "Duplicate STUDENT_ID"),
    ("Check 2: Duplicate College IDs", "RAW_COLLEGES", "select college_id from PLACEMENT_DB.BRONZE.RAW_COLLEGES group by college_id having count(*) > 1", "Duplicate COLLEGE_ID"),
    ("Check 3: Duplicate Company IDs", "RAW_COMPANIES", "select company_id from PLACEMENT_DB.BRONZE.RAW_COMPANIES group by company_id having count(*) > 1", "Duplicate COMPANY_ID"),
    ("Check 4: Duplicate Offer IDs", "RAW_OFFERS", "select offer_id, offer_line_id from PLACEMENT_DB.BRONZE.RAW_OFFERS group by offer_id, offer_line_id having count(*) > 1", "Duplicate offer"),
    ("Check 5: Null Critical Student Fields", "RAW_STUDENTS", "select * from PLACEMENT_DB.BRONZE.RAW_STUDENTS where student_id is null or college_id is null or grad_year is null or cgpa is null", "Null critical fields"),
    ("Check 6: Invalid CGPA", "RAW_STUDENTS", "select * from PLACEMENT_DB.BRONZE.RAW_STUDENTS where cgpa < 0 or cgpa > 10", "Invalid CGPA"),
    ("Check 7: Invalid CTC", "RAW_OFFERS", "select * from PLACEMENT_DB.BRONZE.RAW_OFFERS where ctc_lpa <= 0 or ctc_lpa is null", "Invalid CTC"),
    ("Check 8: Invalid Offer Status", "RAW_OFFERS", "select * from PLACEMENT_DB.BRONZE.RAW_OFFERS where upper(trim(offer_status)) not in ('OFFERED', 'ACCEPTED', 'JOINED', 'REJECTED', 'WITHDRAWN')", "Invalid offer status"),
    ("Check 9: Orphaned Student in Offers", "RAW_OFFERS", "select o.* from PLACEMENT_DB.BRONZE.RAW_OFFERS o left join PLACEMENT_DB.BRONZE.RAW_STUDENTS s on o.student_id = s.student_id where s.student_id is null", "Orphan student"),
    ("Check 10: Orphaned College in Offers", "RAW_OFFERS", "select o.* from PLACEMENT_DB.BRONZE.RAW_OFFERS o left join PLACEMENT_DB.BRONZE.RAW_COLLEGES c on o.college_id = c.college_id where c.college_id is null", "Orphan college"),
    ("Check 11: Orphaned Company in Offers", "RAW_OFFERS", "select o.* from PLACEMENT_DB.BRONZE.RAW_OFFERS o left join PLACEMENT_DB.BRONZE.RAW_COMPANIES c on o.company_id = c.company_id where c.company_id is null", "Orphan company"),
    ("Check 12: Invalid Join Date Order", "RAW_OFFERS", "select * from PLACEMENT_DB.BRONZE.RAW_OFFERS where try_to_date(expected_join_date) < try_to_date(offer_date)", "Join date before offer date"),
    ("Check 13: Star Schema Integrity", "FACT_PLACEMENT", "select f.* from PLACEMENT_DB.GOLD.FACT_PLACEMENT f left join PLACEMENT_DB.GOLD.DIM_STUDENT s on f.sk_student = s.sk_student left join PLACEMENT_DB.GOLD.DIM_COMPANY c on f.sk_company = c.sk_company left join PLACEMENT_DB.GOLD.DIM_COLLEGE cl on f.sk_college = cl.sk_college left join PLACEMENT_DB.GOLD.DIM_DATE d on f.sk_offer_date = d.sk_date where s.sk_student is null or c.sk_company is null or cl.sk_college is null or d.sk_date is null", "Broken foreign key"),
    ("Check 14: SCD2 Consistency", "DIM_STUDENT_AND_COMPANY", "select sk_student::varchar from PLACEMENT_DB.GOLD.DIM_STUDENT where is_current = true and eff_end_ts::date != '9999-12-31'::date union all select sk_company::varchar from PLACEMENT_DB.GOLD.DIM_COMPANY where is_current = true and eff_end_ts::date != '9999-12-31'::date", "Invalid SCD2 active record"),
]

def main():
    batch_id = f"dq_{int(time.time())}"
    conn = get_connection()
    cur = conn.cursor()
    total_violations = 0

    for name, entity, sql, reason in checks:
        cur.execute(sql)
        rows = cur.fetchall()
        status = "PASSED" if not rows else "FAILED"
        print(f"[{status}] {name}: {len(rows)} violations")
        if rows:
            total_violations += len(rows)
            for r in rows:
                cur.execute(
                    "insert into PLACEMENT_DB.OPS.REJECTS (batch_id, entity, source_row, reject_reason) select %s, %s, parse_json(%s), %s",
                    (batch_id, entity, json.dumps([str(x) for x in r]), reason)
                )

    status = "SUCCESS" if total_violations == 0 else "WARNING"
    cur.execute(
        "insert into PLACEMENT_DB.OPS.LOAD_AUDIT (batch_id, file_name, entity, load_ts, row_count, status, error_msg) values (%s, %s, %s, current_timestamp(), %s, %s, %s)",
        (batch_id, "DATA_QUALITY_AUDIT", "ALL_ENTITIES", total_violations, status, f"{total_violations} violations")
    )
    print(f"\nData quality audit finished with {total_violations} violations ({status})")
    cur.close()
    conn.close()

if __name__ == "__main__":
    main()

import sys
import os
import json
from datetime import datetime

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from src.snowflake_connection import get_connection


def run_data_quality_audit():
    batch_id = f"DQ_AUDIT_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    conn = get_connection()
    cur = conn.cursor()

    checks = [
        {
            "name": "Check 1: Duplicate Student IDs in RAW_STUDENTS",
            "entity": "RAW_STUDENTS",
            "sql": """
                SELECT student_id, COUNT(*) as cnt 
                FROM PLACEMENT_DB.BRONZE.RAW_STUDENTS 
                GROUP BY student_id HAVING COUNT(*) > 1
            """,
            "fail_reason": "Duplicate STUDENT_ID found"
        },
        {
            "name": "Check 2: Duplicate College IDs in RAW_COLLEGES",
            "entity": "RAW_COLLEGES",
            "sql": """
                SELECT college_id, COUNT(*) as cnt 
                FROM PLACEMENT_DB.BRONZE.RAW_COLLEGES 
                GROUP BY college_id HAVING COUNT(*) > 1
            """,
            "fail_reason": "Duplicate COLLEGE_ID found"
        },
        {
            "name": "Check 3: Duplicate Company IDs in RAW_COMPANIES",
            "entity": "RAW_COMPANIES",
            "sql": """
                SELECT company_id, COUNT(*) as cnt 
                FROM PLACEMENT_DB.BRONZE.RAW_COMPANIES 
                GROUP BY company_id HAVING COUNT(*) > 1
            """,
            "fail_reason": "Duplicate COMPANY_ID found"
        },
        {
            "name": "Check 4: Duplicate Offer Identifiers in RAW_OFFERS",
            "entity": "RAW_OFFERS",
            "sql": """
                SELECT offer_id, offer_line_id, COUNT(*) as cnt 
                FROM PLACEMENT_DB.BRONZE.RAW_OFFERS 
                GROUP BY offer_id, offer_line_id HAVING COUNT(*) > 1
            """,
            "fail_reason": "Duplicate (OFFER_ID, OFFER_LINE_ID) found"
        },
        {
            "name": "Check 5: Missing Required Student Fields",
            "entity": "RAW_STUDENTS",
            "sql": """
                SELECT * FROM PLACEMENT_DB.BRONZE.RAW_STUDENTS 
                WHERE student_id IS NULL OR college_id IS NULL OR grad_year IS NULL OR cgpa IS NULL
            """,
            "fail_reason": "Null found in critical student column"
        },
        {
            "name": "Check 6: Invalid CGPA Values (< 0 or > 10)",
            "entity": "RAW_STUDENTS",
            "sql": """
                SELECT * FROM PLACEMENT_DB.BRONZE.RAW_STUDENTS 
                WHERE cgpa < 0.0 OR cgpa > 10.0
            """,
            "fail_reason": "CGPA outside valid domain [0.0, 10.0]"
        },
        {
            "name": "Check 7: Invalid CTC Values (<= 0)",
            "entity": "RAW_OFFERS",
            "sql": """
                SELECT * FROM PLACEMENT_DB.BRONZE.RAW_OFFERS 
                WHERE ctc_lpa <= 0 OR ctc_lpa IS NULL
            """,
            "fail_reason": "CTC_LPA is non-positive or null"
        },
        {
            "name": "Check 8: Invalid Offer Statuses",
            "entity": "RAW_OFFERS",
            "sql": """
                SELECT * FROM PLACEMENT_DB.BRONZE.RAW_OFFERS 
                WHERE UPPER(TRIM(offer_status)) NOT IN ('OFFERED', 'ACCEPTED', 'JOINED', 'REJECTED', 'WITHDRAWN')
            """,
            "fail_reason": "Offer status is not an accepted business value"
        },
        {
            "name": "Check 9: Orphaned Student References in Offers",
            "entity": "RAW_OFFERS",
            "sql": """
                SELECT o.* FROM PLACEMENT_DB.BRONZE.RAW_OFFERS o
                LEFT JOIN PLACEMENT_DB.BRONZE.RAW_STUDENTS s ON o.student_id = s.student_id
                WHERE s.student_id IS NULL
            """,
            "fail_reason": "Offer references non-existent STUDENT_ID"
        },
        {
            "name": "Check 10: Orphaned College References in Offers",
            "entity": "RAW_OFFERS",
            "sql": """
                SELECT o.* FROM PLACEMENT_DB.BRONZE.RAW_OFFERS o
                LEFT JOIN PLACEMENT_DB.BRONZE.RAW_COLLEGES c ON o.college_id = c.college_id
                WHERE c.college_id IS NULL
            """,
            "fail_reason": "Offer references non-existent COLLEGE_ID"
        },
        {
            "name": "Check 11: Orphaned Company References in Offers",
            "entity": "RAW_OFFERS",
            "sql": """
                SELECT o.* FROM PLACEMENT_DB.BRONZE.RAW_OFFERS o
                LEFT JOIN PLACEMENT_DB.BRONZE.RAW_COMPANIES c ON o.company_id = c.company_id
                WHERE c.company_id IS NULL
            """,
            "fail_reason": "Offer references non-existent COMPANY_ID"
        },
        {
            "name": "Check 12: Invalid Offer/Join Date Sequence",
            "entity": "RAW_OFFERS",
            "sql": """
                SELECT * FROM PLACEMENT_DB.BRONZE.RAW_OFFERS 
                WHERE TRY_TO_DATE(expected_join_date) < TRY_TO_DATE(offer_date)
            """,
            "fail_reason": "Expected join date is earlier than offer date"
        },
        {
            "name": "Check 13: Star Schema Referential Integrity (FACT_PLACEMENT)",
            "entity": "FACT_PLACEMENT",
            "sql": """
                SELECT f.* FROM PLACEMENT_DB.GOLD.FACT_PLACEMENT f
                LEFT JOIN PLACEMENT_DB.GOLD.DIM_STUDENT s ON f.sk_student = s.sk_student
                LEFT JOIN PLACEMENT_DB.GOLD.DIM_COMPANY c ON f.sk_company = c.sk_company
                LEFT JOIN PLACEMENT_DB.GOLD.DIM_COLLEGE cl ON f.sk_college = cl.sk_college
                LEFT JOIN PLACEMENT_DB.GOLD.DIM_DATE d ON f.sk_offer_date = d.sk_date
                WHERE s.sk_student IS NULL OR c.sk_company IS NULL OR cl.sk_college IS NULL OR d.sk_date IS NULL
            """,
            "fail_reason": "Fact row has broken dimension relationship"
        },
        {
            "name": "Check 14: SCD2 Consistency in DIM_STUDENT & DIM_COMPANY",
            "entity": "DIM_STUDENT",
            "sql": """
                SELECT * FROM PLACEMENT_DB.GOLD.DIM_STUDENT 
                WHERE is_current = TRUE AND eff_end_ts::DATE != '9999-12-31'::DATE
            """,
            "fail_reason": "Current SCD2 record does not have 9999-12-31 end timestamp"
        }
    ]

    print("=" * 60)
    print(f"RUNNING DATA QUALITY & INTEGRITY AUDIT - BATCH: {batch_id}")
    print("=" * 60)

    total_failures = 0

    for c in checks:
        cur.execute(c["sql"])
        rows = cur.fetchall()
        fail_count = len(rows)
        status = "PASSED" if fail_count == 0 else "FAILED"
        print(f"[{status}] {c['name']} - Violations: {fail_count}")

        if fail_count > 0:
            total_failures += fail_count
            for row in rows:
                row_dict = {str(i): str(val) for i, val in enumerate(row)}
                row_json = json.dumps(row_dict)
                cur.execute("""
                    INSERT INTO PLACEMENT_DB.OPS.REJECTS 
                    (BATCH_ID, ENTITY, SOURCE_ROW, REJECT_REASON, REJECTED_AT)
                    SELECT %s, %s, PARSE_JSON(%s), %s, CURRENT_TIMESTAMP()
                """, (batch_id, c["entity"], row_json, c["fail_reason"]))

    overall_status = "SUCCESS" if total_failures == 0 else "WARNING"
    cur.execute("""
        INSERT INTO PLACEMENT_DB.OPS.LOAD_AUDIT 
        (BATCH_ID, FILE_NAME, ENTITY, LOAD_TS, ROW_COUNT, STATUS, ERROR_MSG)
        VALUES (%s, %s, %s, CURRENT_TIMESTAMP(), %s, %s, %s)
    """, (batch_id, "DATA_QUALITY_AUDIT", "ALL_ENTITIES", total_failures, overall_status, f"{total_failures} DQ violations found"))

    print("=" * 60)
    print(f"DQ AUDIT COMPLETE. Total Violations: {total_failures} | Overall: {overall_status}")
    print(f"Audit log recorded in PLACEMENT_DB.OPS.LOAD_AUDIT")
    print("=" * 60)

    cur.close()
    conn.close()
    return total_failures == 0


if __name__ == "__main__":
    run_data_quality_audit()

import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from src.snowflake_connection import get_connection


class TestEndToEndPipeline(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.conn = get_connection()
        cls.cur = cls.conn.cursor()

    @classmethod
    def tearDownClass(cls):
        cls.cur.close()
        cls.conn.close()

    def test_01_snowflake_connection(self):
        self.cur.execute("SELECT CURRENT_DATABASE(), CURRENT_ROLE(), CURRENT_WAREHOUSE()")
        row = self.cur.fetchone()
        self.assertEqual(row[0], "PLACEMENT_DB")
        print(f"  [PASS] Snowflake connected: DB={row[0]}, Role={row[1]}, WH={row[2]}")

    def test_02_bronze_layer_counts(self):
        counts = {
            "RAW_STUDENTS": 20,
            "RAW_COLLEGES": 15,
            "RAW_COMPANIES": 15,
            "RAW_OFFERS": 25
        }
        for table, expected in counts.items():
            self.cur.execute(f"SELECT COUNT(*) FROM PLACEMENT_DB.BRONZE.{table}")
            actual = self.cur.fetchone()[0]
            self.assertEqual(actual, expected)
            print(f"  [PASS] BRONZE.{table}: {actual} rows (Expected {expected})")

    def test_03_silver_layer_counts(self):
        counts = {
            "INT_STUDENTS_CLEANED": 20,
            "INT_COLLEGES_CLEANED": 15,
            "INT_COMPANIES_CLEANED": 15,
            "INT_OFFERS_CLEANED": 25
        }
        for table, expected in counts.items():
            self.cur.execute(f"SELECT COUNT(*) FROM PLACEMENT_DB.SILVER.{table}")
            actual = self.cur.fetchone()[0]
            self.assertEqual(actual, expected)
            print(f"  [PASS] SILVER.{table}: {actual} rows (Expected {expected})")

    def test_04_gold_dimensions_counts(self):
        counts = {
            "DIM_STUDENT": 20,
            "DIM_COMPANY": 15,
            "DIM_COLLEGE": 15,
            "DIM_DATE": 3653
        }
        for table, expected in counts.items():
            self.cur.execute(f"SELECT COUNT(*) FROM PLACEMENT_DB.GOLD.{table}")
            actual = self.cur.fetchone()[0]
            self.assertEqual(actual, expected)
            print(f"  [PASS] GOLD.{table}: {actual} rows (Expected {expected})")

    def test_05_scd2_integrity(self):
        self.cur.execute("SELECT COUNT(*) FROM PLACEMENT_DB.GOLD.DIM_STUDENT WHERE is_current = TRUE AND eff_end_ts::DATE = '9999-12-31'")
        student_current = self.cur.fetchone()[0]
        self.assertEqual(student_current, 20)

        self.cur.execute("SELECT COUNT(*) FROM PLACEMENT_DB.GOLD.DIM_COMPANY WHERE is_current = TRUE AND eff_end_ts::DATE = '9999-12-31'")
        company_current = self.cur.fetchone()[0]
        self.assertEqual(company_current, 15)
        print("  [PASS] SCD Type 2 Integrity: Current records active until 9999-12-31")

    def test_06_fact_placement_grain_and_keys(self):
        self.cur.execute("SELECT COUNT(*), COUNT(DISTINCT sk_fact_placement) FROM PLACEMENT_DB.GOLD.FACT_PLACEMENT")
        total, distinct_keys = self.cur.fetchone()
        self.assertEqual(total, 25)
        self.assertEqual(total, distinct_keys)
        print(f"  [PASS] FACT_PLACEMENT grain verified: {total} total offer rows, all unique SKs")

    def test_07_star_schema_referential_integrity(self):
        self.cur.execute("""
            SELECT COUNT(*) FROM PLACEMENT_DB.GOLD.FACT_PLACEMENT f
            LEFT JOIN PLACEMENT_DB.GOLD.DIM_STUDENT s ON f.sk_student = s.sk_student
            LEFT JOIN PLACEMENT_DB.GOLD.DIM_COMPANY c ON f.sk_company = c.sk_company
            LEFT JOIN PLACEMENT_DB.GOLD.DIM_COLLEGE cl ON f.sk_college = cl.sk_college
            LEFT JOIN PLACEMENT_DB.GOLD.DIM_DATE d ON f.sk_offer_date = d.sk_date
            WHERE s.sk_student IS NULL OR c.sk_company IS NULL OR cl.sk_college IS NULL OR d.sk_date IS NULL
        """)
        orphaned = self.cur.fetchone()[0]
        self.assertEqual(orphaned, 0)
        print("  [PASS] Star Schema Referential Integrity: 0 orphaned foreign keys")

    def test_08_semantic_views(self):
        views = [
            "V_EXECUTIVE_SUMMARY",
            "V_COLLEGE_PERFORMANCE",
            "V_COMPANY_INSIGHTS",
            "V_OFFER_EXPLORER"
        ]
        for v in views:
            self.cur.execute(f"SELECT COUNT(*) FROM PLACEMENT_DB.SEM.{v}")
            cnt = self.cur.fetchone()[0]
            self.assertGreater(cnt, 0)
            print(f"  [PASS] SEM.{v}: Query successful ({cnt} rows)")

    def test_09_kpi_calculations(self):
        self.cur.execute("SELECT total_offers, avg_ctc, placement_rate_pct FROM PLACEMENT_DB.SEM.V_EXECUTIVE_SUMMARY")
        row = self.cur.fetchone()
        self.assertEqual(row[0], 25)
        self.assertAlmostEqual(float(row[1]), 26.19, delta=0.1)
        self.assertAlmostEqual(float(row[2]), 41.67, delta=0.1)
        print(f"  [PASS] Executive KPIs Verified: Offers={row[0]}, Avg CTC={row[1]} LPA, Placement Rate={row[2]}%")

    def test_10_operational_audit_logging(self):
        self.cur.execute("SELECT COUNT(*) FROM PLACEMENT_DB.OPS.LOAD_AUDIT WHERE status = 'SUCCESS'")
        success_count = self.cur.fetchone()[0]
        self.assertGreater(success_count, 0)
        print(f"  [PASS] OPS.LOAD_AUDIT verified: {success_count} successful audit events recorded")


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("RUNNING END-TO-END VERIFICATION SUITE")
    print("=" * 60)
    unittest.main()

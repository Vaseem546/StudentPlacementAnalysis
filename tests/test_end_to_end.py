import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from src.snowflake_connection import get_connection

class TestPlacementPipeline(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.conn = get_connection()
        cls.cur = cls.conn.cursor()

    @classmethod
    def tearDownClass(cls):
        cls.cur.close()
        cls.conn.close()

    def test_01_connection(self):
        self.cur.execute("select current_database()")
        self.assertEqual(self.cur.fetchone()[0], "PLACEMENT_DB")

    def test_02_bronze_counts(self):
        counts = {"RAW_STUDENTS": 20, "RAW_COLLEGES": 15, "RAW_COMPANIES": 15, "RAW_OFFERS": 25}
        for table, expected in counts.items():
            self.cur.execute(f"select count(*) from PLACEMENT_DB.BRONZE.{table}")
            self.assertEqual(self.cur.fetchone()[0], expected)

    def test_03_silver_counts(self):
        counts = {"INT_STUDENTS_CLEANED": 20, "INT_COLLEGES_CLEANED": 15, "INT_COMPANIES_CLEANED": 15, "INT_OFFERS_CLEANED": 25}
        for table, expected in counts.items():
            self.cur.execute(f"select count(*) from PLACEMENT_DB.SILVER.{table}")
            self.assertEqual(self.cur.fetchone()[0], expected)

    def test_04_gold_dimension_counts(self):
        counts = {"DIM_STUDENT": 20, "DIM_COMPANY": 15, "DIM_COLLEGE": 15, "DIM_DATE": 3653}
        for table, expected in counts.items():
            self.cur.execute(f"select count(*) from PLACEMENT_DB.GOLD.{table}")
            self.assertEqual(self.cur.fetchone()[0], expected)

    def test_05_scd2_integrity(self):
        self.cur.execute("select count(*) from PLACEMENT_DB.GOLD.DIM_STUDENT where is_current = true and eff_end_ts::date = '9999-12-31'")
        self.assertEqual(self.cur.fetchone()[0], 20)
        self.cur.execute("select count(*) from PLACEMENT_DB.GOLD.DIM_COMPANY where is_current = true and eff_end_ts::date = '9999-12-31'")
        self.assertEqual(self.cur.fetchone()[0], 15)

    def test_06_fact_placement_grain(self):
        self.cur.execute("select count(*), count(distinct sk_fact_placement) from PLACEMENT_DB.GOLD.FACT_PLACEMENT")
        total, distinct_sks = self.cur.fetchone()
        self.assertEqual(total, 25)
        self.assertEqual(total, distinct_sks)

    def test_07_star_schema_integrity(self):
        self.cur.execute("""
            select count(*) from PLACEMENT_DB.GOLD.FACT_PLACEMENT f
            left join PLACEMENT_DB.GOLD.DIM_STUDENT s on f.sk_student = s.sk_student
            left join PLACEMENT_DB.GOLD.DIM_COMPANY c on f.sk_company = c.sk_company
            left join PLACEMENT_DB.GOLD.DIM_COLLEGE cl on f.sk_college = cl.sk_college
            left join PLACEMENT_DB.GOLD.DIM_DATE d on f.sk_offer_date = d.sk_date
            where s.sk_student is null or c.sk_company is null or cl.sk_college is null or d.sk_date is null
        """)
        self.assertEqual(self.cur.fetchone()[0], 0)

    def test_08_semantic_views(self):
        for v in ["V_EXECUTIVE_SUMMARY", "V_COLLEGE_PERFORMANCE", "V_COMPANY_INSIGHTS", "V_OFFER_EXPLORER"]:
            self.cur.execute(f"select count(*) from PLACEMENT_DB.SEM.{v}")
            self.assertGreater(self.cur.fetchone()[0], 0)

    def test_09_kpis(self):
        self.cur.execute("select total_offers, avg_ctc, placement_rate_pct from PLACEMENT_DB.SEM.V_EXECUTIVE_SUMMARY")
        row = self.cur.fetchone()
        self.assertEqual(row[0], 25)
        self.assertAlmostEqual(float(row[1]), 26.19, delta=0.1)
        self.assertAlmostEqual(float(row[2]), 41.67, delta=0.1)

    def test_10_audit_log(self):
        self.cur.execute("select count(*) from PLACEMENT_DB.OPS.LOAD_AUDIT where status = 'SUCCESS'")
        self.assertGreater(self.cur.fetchone()[0], 0)

if __name__ == "__main__":
    unittest.main()

import os, sys, logging
from datetime import datetime
from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql.types import *

os.makedirs("data/cleaned", exist_ok=True)
os.makedirs("logs", exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.FileHandler("logs/pyspark_pipeline.log"), logging.StreamHandler(sys.stdout)],
)
log = logging.getLogger(__name__)

SCHEMAS = {
    "students": StructType([
        StructField("STUDENT_ID", StringType()), StructField("FIRST_NAME", StringType()),
        StructField("LAST_NAME", StringType()),  StructField("GENDER", StringType()),
        StructField("DOB", StringType()),         StructField("COLLEGE_ID", StringType()),
        StructField("PROGRAM", StringType()),     StructField("BRANCH", StringType()),
        StructField("GRAD_YEAR", IntegerType()),  StructField("CGPA", DoubleType()),
        StructField("CITY", StringType()),        StructField("STATE", StringType()),
        StructField("COUNTRY", StringType()),     StructField("SEGMENT", StringType()),
        StructField("UPDATED_AT", StringType()),
    ]),
    "colleges": StructType([
        StructField("COLLEGE_ID", StringType()),       StructField("COLLEGE_NAME", StringType()),
        StructField("CITY", StringType()),             StructField("STATE", StringType()),
        StructField("COUNTRY", StringType()),          StructField("OWNERSHIP", StringType()),
        StructField("TIER", StringType()),             StructField("CATEGORY", StringType()),
        StructField("ESTABLISHED_DATE", StringType()), StructField("STATUS", StringType()),
    ]),
    "companies": StructType([
        StructField("COMPANY_ID", StringType()),    StructField("COMPANY_NAME", StringType()),
        StructField("INDUSTRY", StringType()),      StructField("HQ_COUNTRY", StringType()),
        StructField("SIZE_BAND", StringType()),     StructField("HIRING_CITY", StringType()),
        StructField("HIRING_STATE", StringType()),  StructField("STATUS", StringType()),
        StructField("PARTNER_SINCE", StringType()), StructField("UPDATED_AT", StringType()),
    ]),
    "offers": StructType([
        StructField("OFFER_ID", StringType()),           StructField("OFFER_LINE_ID", IntegerType()),
        StructField("OFFER_DATE", StringType()),         StructField("EXPECTED_JOIN_DATE", StringType()),
        StructField("STUDENT_ID", StringType()),         StructField("COMPANY_ID", StringType()),
        StructField("COLLEGE_ID", StringType()),         StructField("ROLE_TITLE", StringType()),
        StructField("OFFER_LEVEL", StringType()),        StructField("CTC_LPA", DoubleType()),
        StructField("MONTHLY_STIPEND", DoubleType()),    StructField("JOB_CITY", StringType()),
        StructField("HIRING_MODE", StringType()),        StructField("OFFER_STATUS", StringType()),
        StructField("IS_JOINED", IntegerType()),         StructField("UPDATED_AT", StringType()),
    ]),
}

VALID = {
    "PROGRAM":       {"B.Tech", "M.Tech", "MBA"},
    "OFFER_STATUS":  {"OFFERED", "ACCEPTED", "JOINED", "REJECTED", "WITHDRAWN"},
    "OFFER_LEVEL":   {"FTE", "INTERN"},
    "HIRING_MODE":   {"ON_CAMPUS", "OFF_CAMPUS", "REFERRAL"},
}


def get_spark():
    spark = SparkSession.builder.appName("PlacementPipeline") \
        .config("spark.sql.legacy.timeParserPolicy", "LEGACY").getOrCreate()
    spark.sparkContext.setLogLevel("WARN")
    return spark


def profile_and_check(df, name, pk):
    log.info(f"[{name}] rows={df.count()}")
    nulls = {c: df.filter(F.col(c).isNull()).count() for c in df.columns}
    for c, n in nulls.items():
        if n: log.warning(f"  [{name}] {c}: {n} nulls")
    dups = df.groupBy(pk).count().filter(F.col("count") > 1).count()
    log.info(f"  [{name}] duplicates on {pk}: {dups}")


def clean_students(df):
    rejects = df.filter(
        F.col("STUDENT_ID").isNull() | F.col("CGPA").isNull() |
        (F.col("CGPA") < 0) | (F.col("CGPA") > 10) |
        ~F.col("PROGRAM").isin(list(VALID["PROGRAM"]))
    )
    clean = df.subtract(rejects) \
        .withColumn("GENDER",   F.upper(F.trim("GENDER"))) \
        .withColumn("SEGMENT",  F.upper(F.trim("SEGMENT"))) \
        .withColumn("BRANCH",   F.upper(F.trim("BRANCH"))) \
        .withColumn("CGPA_BAND",
            F.when(F.col("CGPA") >= 9.0, "9+")
             .when(F.col("CGPA") >= 8.0, "8-9")
             .when(F.col("CGPA") >= 7.0, "7-8")
             .when(F.col("CGPA") >= 6.0, "6-7")
             .otherwise("<6")) \
        .withColumn("UPDATED_AT", F.to_timestamp("UPDATED_AT"))
    return clean, rejects


def clean_colleges(df):
    rejects = df.filter(F.col("COLLEGE_ID").isNull() | F.col("COLLEGE_NAME").isNull())
    clean = df.subtract(rejects) \
        .withColumn("OWNERSHIP", F.initcap(F.trim("OWNERSHIP"))) \
        .withColumn("STATUS",    F.upper(F.trim("STATUS")))
    return clean, rejects


def clean_companies(df):
    rejects = df.filter(F.col("COMPANY_ID").isNull() | F.col("COMPANY_NAME").isNull())
    clean = df.subtract(rejects) \
        .withColumn("STATUS",    F.upper(F.trim("STATUS"))) \
        .withColumn("SIZE_BAND", F.initcap(F.trim("SIZE_BAND"))) \
        .withColumn("UPDATED_AT", F.to_timestamp("UPDATED_AT"))
    return clean, rejects


def clean_offers(df, student_ids, college_ids, company_ids):
    rejects = df.filter(
        F.col("OFFER_ID").isNull() | F.col("CTC_LPA").isNull() | (F.col("CTC_LPA") < 0) |
        ~F.col("OFFER_STATUS").isin(list(VALID["OFFER_STATUS"])) |
        ~F.col("OFFER_LEVEL").isin(list(VALID["OFFER_LEVEL"])) |
        ~F.col("HIRING_MODE").isin(list(VALID["HIRING_MODE"])) |
        ~F.col("STUDENT_ID").isin(student_ids) |
        ~F.col("COLLEGE_ID").isin(college_ids) |
        ~F.col("COMPANY_ID").isin(company_ids)
    )
    clean = df.subtract(rejects) \
        .withColumn("OFFER_DATE",         F.to_date("OFFER_DATE")) \
        .withColumn("EXPECTED_JOIN_DATE", F.to_date("EXPECTED_JOIN_DATE")) \
        .withColumn("UPDATED_AT",         F.to_timestamp("UPDATED_AT")) \
        .withColumn("MONTHLY_STIPEND",    F.coalesce(F.col("MONTHLY_STIPEND"), F.lit(0.0)))
    return clean, rejects


def save(df, name):
    path = f"data/cleaned/{name}.csv"
    df.toPandas().to_csv(path, index=False)
    log.info(f"[{name}] {df.count()} clean records saved -> {path}")


def main():
    spark = get_spark()
    log.info(f"Pipeline started at {datetime.now()}")

    results = {}
    for name in ["students", "colleges", "companies", "offers"]:
        df = spark.read.csv(f"data/placement_{name}.csv", schema=SCHEMAS[name], header=True)
        profile_and_check(df, name.upper(), list(SCHEMAS[name].fieldNames())[0])
        results[name] = df

    s_clean, _ = clean_students(results["students"])
    cl_clean, _ = clean_colleges(results["colleges"])
    co_clean, _ = clean_companies(results["companies"])

    s_ids  = [r.STUDENT_ID  for r in s_clean.select("STUDENT_ID").collect()]
    cl_ids = [r.COLLEGE_ID  for r in cl_clean.select("COLLEGE_ID").collect()]
    co_ids = [r.COMPANY_ID  for r in co_clean.select("COMPANY_ID").collect()]

    of_clean, _ = clean_offers(results["offers"], s_ids, cl_ids, co_ids)

    for name, df in [("students", s_clean), ("colleges", cl_clean),
                     ("companies", co_clean), ("offers", of_clean)]:
        save(df, name)

    log.info("-- SUMMARY --")
    of_clean.groupBy("OFFER_STATUS").count().orderBy("OFFER_STATUS").show()
    s_clean.groupBy("CGPA_BAND").count().orderBy("CGPA_BAND").show()

    ctc = of_clean.agg(F.round(F.min("CTC_LPA"),2).alias("min"),
                       F.round(F.max("CTC_LPA"),2).alias("max"),
                       F.round(F.avg("CTC_LPA"),2).alias("avg")).collect()[0]
    log.info(f"CTC -> min={ctc['min']}  max={ctc['max']}  avg={ctc['avg']} LPA")
    log.info(f"Pipeline completed at {datetime.now()}")
    spark.stop()


if __name__ == "__main__":
    main()

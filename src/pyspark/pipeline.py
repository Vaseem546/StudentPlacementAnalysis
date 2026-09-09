import os
from pyspark.sql import SparkSession
from pyspark.sql import functions as F

os.makedirs("data/cleaned", exist_ok=True)

spark = SparkSession.builder.appName("PlacementPipeline").getOrCreate()
spark.sparkContext.setLogLevel("ERROR")

# load csv data
students = spark.read.csv("data/placement_students.csv", header=True, inferSchema=True)
colleges = spark.read.csv("data/placement_colleges.csv", header=True, inferSchema=True)
companies = spark.read.csv("data/placement_companies.csv", header=True, inferSchema=True)
offers = spark.read.csv("data/placement_offers.csv", header=True, inferSchema=True)

# clean students
valid_programs = ["B.Tech", "M.Tech", "MBA"]
clean_students = students.filter(
    (F.col("STUDENT_ID").isNotNull()) &
    (F.col("CGPA").isNotNull()) &
    (F.col("CGPA") >= 0) & (F.col("CGPA") <= 10) &
    (F.col("PROGRAM").isin(valid_programs))
).withColumn("GENDER", F.upper(F.trim("GENDER"))) \
 .withColumn("SEGMENT", F.upper(F.trim("SEGMENT"))) \
 .withColumn("BRANCH", F.upper(F.trim("BRANCH"))) \
 .withColumn("CGPA_BAND",
    F.when(F.col("CGPA") >= 9.0, "9+")
     .when(F.col("CGPA") >= 8.0, "8-9")
     .when(F.col("CGPA") >= 7.0, "7-8")
     .when(F.col("CGPA") >= 6.0, "6-7")
     .otherwise("<6"))

# clean colleges
clean_colleges = colleges.filter(
    (F.col("COLLEGE_ID").isNotNull()) & (F.col("COLLEGE_NAME").isNotNull())
).withColumn("OWNERSHIP", F.initcap(F.trim("OWNERSHIP"))) \
 .withColumn("STATUS", F.upper(F.trim("STATUS")))

# clean companies
clean_companies = companies.filter(
    (F.col("COMPANY_ID").isNotNull()) & (F.col("COMPANY_NAME").isNotNull())
).withColumn("STATUS", F.upper(F.trim("STATUS"))) \
 .withColumn("SIZE_BAND", F.initcap(F.trim("SIZE_BAND")))

# clean offers
s_ids = [r[0] for r in clean_students.select("STUDENT_ID").collect()]
cl_ids = [r[0] for r in clean_colleges.select("COLLEGE_ID").collect()]
co_ids = [r[0] for r in clean_companies.select("COMPANY_ID").collect()]

valid_statuses = ["OFFERED", "ACCEPTED", "JOINED", "REJECTED", "WITHDRAWN"]
valid_levels = ["FTE", "INTERN"]
valid_modes = ["ON_CAMPUS", "OFF_CAMPUS", "REFERRAL"]

clean_offers = offers.filter(
    (F.col("OFFER_ID").isNotNull()) &
    (F.col("CTC_LPA").isNotNull()) & (F.col("CTC_LPA") >= 0) &
    (F.col("OFFER_STATUS").isin(valid_statuses)) &
    (F.col("OFFER_LEVEL").isin(valid_levels)) &
    (F.col("HIRING_MODE").isin(valid_modes)) &
    (F.col("STUDENT_ID").isin(s_ids)) &
    (F.col("COLLEGE_ID").isin(cl_ids)) &
    (F.col("COMPANY_ID").isin(co_ids))
).withColumn("MONTHLY_STIPEND", F.coalesce(F.col("MONTHLY_STIPEND"), F.lit(0.0)))

# save cleaned files
for name, df in [("students", clean_students), ("colleges", clean_colleges),
                 ("companies", clean_companies), ("offers", clean_offers)]:
    df.toPandas().to_csv(f"data/cleaned/{name}.csv", index=False)
    print(f"Saved {name}: {df.count()} rows")

spark.stop()

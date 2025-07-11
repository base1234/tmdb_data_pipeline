import os
import json
import glob
import subprocess
from pyspark.sql import SparkSession
from pyspark.sql.functions import explode, col

# --- Step 1: Validate JSON Files ---
RAW_DIR = "data/raw"
FILES = glob.glob(f"{RAW_DIR}/*.json")

if not FILES:
    raise FileNotFoundError("No JSON files found in data/raw/")

print(f"✅ Found {len(FILES)} files. Validating...")

for file in FILES:
    with open(file, "r") as f:
        data = json.load(f)
        if "results" not in data:
            raise ValueError(f"'results' field missing in: {file}")
        if not isinstance(data["results"], list):
            raise ValueError(f"'results' is not a list in: {file}")
print("✅ All files passed JSON structure validation.")

# --- Step 2: Run Spark ETL ---
print("🚀 Starting Spark ETL...")

spark = SparkSession.builder.appName("TMDB Spark ETL").getOrCreate()

df = spark.read.json(FILES)
df = df.selectExpr("explode(results) as movie")

flat_df = df.select(
    col("movie.id").alias("movie_id"),
    col("movie.title"),
    col("movie.release_date"),
    col("movie.vote_average"),
    explode(col("movie.genre_ids")).alias("genre_id")
)

os.makedirs("data/processed", exist_ok=True)
flat_df.write.mode("overwrite").parquet("data/processed/movies.parquet")
print("✅ ETL complete. Output written to data/processed/movies.parquet")

spark.stop()

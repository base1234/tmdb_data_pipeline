import os
import glob
from pyspark.sql import SparkSession

# Initialize Spark session
spark = SparkSession.builder \
    .appName("InspectSchema") \
    .getOrCreate()

# Resolve full paths using glob instead of Spark wildcards
RAW_DATA_DIR = os.path.join(os.getcwd(), "data", "raw")
json_files = glob.glob(os.path.join(RAW_DATA_DIR, "movies_popular_*.json"))

if not json_files:
    raise FileNotFoundError(f"No JSON files found in: {RAW_DATA_DIR}")

# Read data
df = spark.read.json(json_files)

# Print schema
df.printSchema()

# Optional: show sample rows to verify structure
df.show(5, truncate=False)

# Stop Spark session
spark.stop()


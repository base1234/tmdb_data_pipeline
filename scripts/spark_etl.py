from pyspark.sql import SparkSession
from pyspark.sql.functions import explode, col
import os

# Initialize Spark session
spark = SparkSession.builder.appName("TMDB Spark ETL").getOrCreate()

# Define paths
input_path = "/home/srik1/tmdb_data_pipeline/data/raw"
output_path = "/home/srik1/tmdb_data_pipeline/data/processed"

# Read JSON files with multiline support
df = spark.read.option("multiLine", True).json(input_path)

# Check for results field
if "results" not in df.columns:
    raise ValueError("No 'results' field found. Ensure ingestion script writes full JSON response.")

# Explode the results array
movies_df = df.select(explode(col("results")).alias("movie"))

# Select and flatten all relevant movie fields
flat_df = movies_df.select(
    col("movie.adult").alias("adult"),
    col("movie.backdrop_path").alias("backdrop_path"),
    explode(col("movie.genre_ids")).alias("genre_id"),
    col("movie.id").alias("movie_id"),
    col("movie.original_language").alias("original_language"),
    col("movie.original_title").alias("original_title"),
    col("movie.overview").alias("overview"),
    col("movie.popularity").alias("popularity"),
    col("movie.poster_path").alias("poster_path"),
    col("movie.release_date").alias("release_date"),
    col("movie.title").alias("title"),
    col("movie.video").alias("video"),
    col("movie.vote_average").alias("vote_average"),
    col("movie.vote_count").alias("vote_count")
)

# Write to Parquet
flat_df.write.mode("overwrite").parquet(f"{output_path}/movies.parquet")
print(f"✅ ETL complete. Output written to {output_path}/movies.parquet")

#df1 = spark.read.parquet("data/processed/movies.parquet")
#df1.show(5, truncate=False)
#df1.printSchema()
spark.stop()

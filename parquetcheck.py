import
df = spark.read.parquet("data/processed/movies.parquet")
df.show(5, truncate=False)
df.printSchema()

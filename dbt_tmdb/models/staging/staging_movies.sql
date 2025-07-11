-- This staging model reads Parquet files written by the Spark ETL job.
-- It flattens and standardizes schema so it's easy to join and query later

SELECT *
FROM read_parquet('/home/srik1/tmdb_data_pipeline/data/processed/movies.parquet/*.parquet')

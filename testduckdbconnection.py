import duckdb
import pandas as pd

# Path to your DuckDB file
DB_PATH = "tmdb.duckdb"

# Connect to the DuckDB database
try:
    conn = duckdb.connect(DB_PATH)
    print(f"✅ Connected to database: {DB_PATH}")
except Exception as e:
    print(f"❌ Failed to connect to DuckDB: {e}")
    exit(1)

# List all tables
try:
    tables = conn.execute("SHOW TABLES").fetchall()
    print("\n📄 Tables in database:")
    for t in tables:
        print(" -", t[0])
except Exception as e:
    print(f"❌ Failed to list tables: {e}")
    exit(1)

# Try joining staging_movies with genre_lookup
query = """
SELECT 
    m.title,
    m.release_date,
    CAST(substr(m.release_date, 1, 4) AS INTEGER) AS release_year,
    m.vote_average,
    m.vote_count,
    m.popularity,
    g.genre_name
FROM staging_movies m
LEFT JOIN genre_lookup g ON m.genre_id = g.genre_id
LIMIT 5
"""

try:
    df = conn.execute(query).fetchdf()
    print("\n✅ Sample output from joined query:")
    print(df)
except Exception as e:
    print(f"\n❌ Query failed: {e}")

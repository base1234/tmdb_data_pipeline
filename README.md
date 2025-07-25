# TMDB Data Pipeline

This project builds a simple end-to-end data pipeline using TMDB's movie dataset. It includes data ingestion, transformation, and modeling using Python, PySpark, Airflow, and DBT. The pipeline processes raw JSON files into structured Parquet files and applies transformations to make them analytics-ready.

---

## 🛠️ Tools & Technologies Used

- Python
- Airflow
- PySpark
- DBT (Data Build Tool)
- DuckDB (Local Data Warehouse)

---

## 📁 Project Structure
```
├── README.md
├── airflow
│   ├── airflow.cfg
│   ├── airflow.db
│   ├── dags
│   ├── logs
│   └── simple_auth_manager_passwords.json.generated
├── artifacts
├── data
│   ├── processed
│   ├── raw
│   └── warehouse
├── dbt_tmdb
│   ├── dbt_project.yml
│   ├── logs
│   ├── macros
│   ├── models
│   ├── seeds
│   ├── snapshots
│   └── target
├── docker
│   ├── Dockerfile
│   └── docker-compose.yml
├── logs
│   └── dbt.log
├── moviedashboard.py
├── my_script.py
├── notebooks
│   └── analyze_movies.ipynb
├── parquetcheck.py
├── requirements.txt
├── scripts
│   ├── __pycache__
│   ├── artifacts
│   ├── data
│   ├── fetch_genres.py
│   ├── flatten_json.py
│   ├── ingest_tmdb.py
│   ├── inspect_schema.py
│   ├── print_paths.py
│   ├── run_etl_with_validation.py
│   ├── spark_etl.py
│   └── utils.py
├── setup.sh
├── spark-4.0.0-bin-hadoop3.tgz.1
├── streamlit-venv
│   ├── bin
│   ├── etc
│   ├── include
│   ├── lib
│   ├── lib64 -> lib
│   ├── pyvenv.cfg
│   └── share
├── superset
│   ├── create_admin.py
│   ├── dashboard_config.json
│   └── superset_config
├── superset-venv
│   ├── bin
│   ├── include
│   ├── lib
│   ├── lib64 -> lib
│   └── pyvenv.cfg
├── testduckdbconnection.py
├── tmdb.duckdb
└── venv
    ├── bin
    ├── include
    ├── lib
    ├── lib64 -> lib
    ├── pyvenv.cfg
    └── share
```
---

## ⚙️ Airflow DAG Overview

`tmdb_pipeline.py` DAG performs the following steps:

1. `fetch_genres`: Fetches genre metadata from the TMDB API.
2. `ingest_movies`: Ingests popular movie data and stores it in JSON.
3. `run_spark_etl`: Reads raw JSONs and flattens/explodes the data using PySpark.
4. `run_dbt`: Seeds DuckDB with static files and runs transformation models.

---

## 🧪 Manual Testing (Before Automation)

You can manually test scripts using:
```bash
python scripts/fetch_genres.py
python scripts/ingest_tmdb.py
spark-submit scripts/spark_etl.py
dbt seed
dbt run
```

---

## 📌 Airflow Setup & Execution

1. **Create a virtual environment**
```bash
python -m venv venv
source venv/bin/activate
```

2. **Install Airflow and requirements**
```bash
pip install apache-airflow
```

3. **Create Airflow structure**
```bash
mkdir airflow airflow/dags
```

4. **Add your DAG to `airflow/dags/tmdb_pipeline.py`**

5. **Initialize Airflow DB**
```bash
airflow db init
```

6. **Run Airflow webserver**
```bash
airflow standalone
```

---

## ⚡ PySpark Script (ETL)

`spark_etl.py`:
- Reads raw JSON
- Explodes `results`
- Normalizes fields
- Saves as Parquet to `data/processed`

---

## 🧱 DBT Setup

1. Initialize DBT project:
```bash
cd dbt_tmdb
dbt init .
```

2. Configure `profiles.yml` to use DuckDB.

3. Define staging and modeling SQLs inside `models/`.

4. Seed & run models:
```bash
dbt seed
dbt run
```

---

## 💡 Optional Enhancements

- Add Superset or Streamlit dashboard for final visualizations
- Schedule DAG with a weekly interval
- Store raw/processed data in cloud storage (e.g., GCS or S3)


# 🎬 TMDB Movie Dashboard

An interactive movie analytics dashboard powered by **Streamlit** and **DuckDB**. Visualize and explore TMDB movie metadata by genre, rating, year, and popularity.

---

## 🚀 Features

- ⚡ Fast, local SQL queries using **DuckDB**
- 🎨 Built with **Streamlit** (dark mode)
- 📈 KPIs for average rating, popularity, and vote count
- 📊 Visuals:
  - Scatter plot: Popularity vs. Vote Count
  - Bar chart: Average Rating by Genre
  - Bar chart: Movie Count by Genre
  - Line chart: Yearly Average Ratings
- 🧩 Interactive filters by genre and release year
- 📂 Expandable raw movie data view
- 🔁 Deduplication logic for movies with multiple genres

---

## 🗂️ Database Schema

Ensure your `tmdb.duckdb` file contains the following tables:

| Table Name          | Description                              |
|---------------------|------------------------------------------|
| `genre_lookup`      | Maps `genre_id` to `genre_name`          |
| `genres`            | Same as above, used for cross-checking   |
| `staging_movies`    | Raw TMDB movie data                      |
| `top_genres`        | Pre-aggregated genre stats               |
| `top_movies`        | Top movies with vote averages            |
| `yearly_avg_ratings`| Average ratings aggregated by year       |

### `staging_movies` key columns:
| Column            | Type    |
|-------------------|---------|
| `movie_id`        | BIGINT  |
| `title`           | VARCHAR |
| `release_date`    | VARCHAR |
| `vote_average`    | DOUBLE  |
| `vote_count`      | BIGINT  |
| `popularity`      | DOUBLE  |
| `genre_id`        | BIGINT  |

---

## 🛠️ Setup Instructions

### 1. Clone the repository
```bash
git clone <your-repo-url>
cd tmdb_data_pipeline
```

### 2. Create & activate a virtual environment
```bash
python3 -m venv streamlit-venv
source streamlit-venv/bin/activate   # Windows: .\streamlit-venv\Scripts\activate
```

### 3. Install required dependencies
```bash
pip install streamlit duckdb pandas plotly
```

### 4. Verify your DuckDB database
Ensure `tmdb.duckdb` exists in the project root and contains the required tables.

### 5. Run the dashboard
```bash
streamlit run moviedashboard.py
```

---

## ⚙️ Release Year Parsing Logic

To avoid conversion errors when extracting years from poorly formatted dates, this logic is applied:

```sql
CASE 
  WHEN length(release_date) >= 4 
   AND substr(release_date, 1, 4) GLOB '[0-9][0-9][0-9][0-9]'
  THEN CAST(substr(release_date, 1, 4) AS INTEGER)
  ELSE NULL
END AS release_year
```

---

## 💡 Use Cases

- Discover which genres dominate in popularity or rating
- Analyze trends over years for movie ratings
- Compare audience vote volume vs. perceived popularity
- Monitor newly released movies and how they perform

---

## 📸 Screenshots of Dashboard
![Screenshot 1](Screenshot%202025-07-24%20203010.png)
![Screenshot 2](Screenshot%202025-07-24%20203034.png)
![Screenshot 3](Screenshot%202025-07-24%20203057.png)
![Screenshot 4](Screenshot%202025-07-24%20203124.png)
![Screenshot 5](Screenshot%202025-07-24%20203229.png)


---

## 📌 Notes

- One movie can belong to multiple genres (join logic accounts for this)
- The dashboard uses deduplication logic where needed for KPIs and trends
- Visual layout is structured into sections: KPIs, filters, plots, and raw data

---

## 📄 License

MIT License (add full license text here if open-sourcing)

---

## 🙋‍♂️ Contributing

PRs are welcome. For major changes, please open an issue first to discuss what you’d like to change or enhance.


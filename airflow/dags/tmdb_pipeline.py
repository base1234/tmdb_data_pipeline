from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta
from pathlib import Path
import sys

# Dynamically determine absolute paths
BASE_DIR = Path("/home/srik1/tmdb_data_pipeline")
SCRIPTS_DIR = BASE_DIR / "scripts"
DBT_DIR = BASE_DIR / "dbt_tmdb"

# Add scripts folder to Python path
sys.path.append(str(SCRIPTS_DIR))

# Import fetch function from script
from fetch_genres import fetch_and_save_genres
from ingest_tmdb import fetch_popular_movies

default_args = {
    "owner": "airflow",
    "start_date": datetime(2024, 1, 1),
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}

with DAG(
    dag_id="tmdb_data_pipeline",
    default_args=default_args,
    schedule=None,
    catchup=False
) as dag:

    print_env_task = BashOperator(
        task_id="print_env",
        bash_command="echo 'PWD:' $(pwd) && echo 'LS:' && ls -alh /home/srik1/tmdb_data_pipeline/data"
    )

    fetch_genres_task = PythonOperator(
        task_id="fetch_genres",
        python_callable=fetch_and_save_genres
    )

    ingest_task = PythonOperator(
        task_id="ingest_movies",
        python_callable=fetch_popular_movies
    )

    spark_etl_task = BashOperator(
        task_id="run_spark_etl",
        bash_command=f"echo 'Running Spark ETL in:' $(pwd) && spark-submit {SCRIPTS_DIR / 'spark_etl.py'}"
    )

    dbt_run_task = BashOperator(
        task_id="run_dbt",
        bash_command=f"cd {DBT_DIR} && dbt seed && dbt run"
    )

    print_env_task >> fetch_genres_task >> ingest_task >> spark_etl_task >> dbt_run_task

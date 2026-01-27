from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime

default_args = {
    "owner": "nexon",
    "start_date": datetime(2025, 1, 1),
    "retries": 1
}

with DAG(
    dag_id="spark_pipeline",
    default_args=default_args,
    schedule_interval="@daily",
    catchup=False
) as dag:

    run_spark = BashOperator(
        task_id="run_sentiment",
        bash_command="docker exec spark_runner python /opt/project/spark/spark_sentiment.py"
    )

    run_spark

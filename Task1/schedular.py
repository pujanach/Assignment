from datetime import datetime, timedelta

import pendulum
from airflow import DAG
from airflow.operators.bash import BashOperator

default_args = {
    "owner": "Pujan Acharya",
    "depends_on_past": False,
    "start_date": "2024-01-01",
    "retries": 2,
}

with DAG(
    dag_id="Weekly_Crawler",
    default_args=default_args,
    catchup=False,
    schedule_interval="0 0 * * 0",
) as dag:

    crawling = BashOperator(task_id="crawl", bash_command="python crawler.py")

    searching = BashOperator(
        task_id="searching", bash_command="python search.py")


crawling >> searching

from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python_operator import PythonOperator


default_args = {
    'owner': 'jessica',
    'depends_on_past': False,
    'start_date': datetime(2022, 1, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}


dag = DAG(
    dag_id = 'spark_project_dag',
    description='Dag for a sql spark project',
    tags=['jessica', 'spark'],
    default_args=default_args,
    schedule_interval='@daily',  # Set your desired schedule
    catchup=False,
)

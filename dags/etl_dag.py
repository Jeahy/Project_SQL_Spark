from datetime import datetime, timedelta
import sys
sys.path.append('/home/pkn/ecompipeline/')

from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from scripts.config import input_raw, output_transformed
from scripts.download_data_script import download_data_main
from scripts.imp_clean_trans_script import clean_transform_main


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


download_data_task = PythonOperator(
    task_id = 'download_data',
    python_callable = download_data_main,
    provide_context=True,  # Pass the Airflow context to the function
    dag = dag,
)

import_clean_transform_task = PythonOperator(
    task_id = 'import_clean_transform',
    python_callable = clean_transform_main,
    op_args=[input_raw, output_transformed],
    provide_context=True,  # Pass the Airflow context to the function
    dag = dag,
)


download_data_task >> import_clean_transform_task
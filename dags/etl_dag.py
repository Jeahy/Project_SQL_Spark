from datetime import datetime, timedelta
import sys
sys.path.append('/home/pkn/ecompipeline/')

from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from scripts.config import input_raw, output_transformed, db_url, user, password, host, port, new_db_name
from scripts.download_data_script import download_data_main
from scripts.imp_clean_trans_script import clean_transform_main
from scripts.validate_data_script import validate_data_main
from scripts.create_db_script import create_db_main
from scripts.create_tables_script import create_tables_main
from scripts.load_data_script import load_data_main



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

validate_data_task = PythonOperator(
    task_id = 'validate_data',
    python_callable = validate_data_main,
    op_args=[output_transformed],
    provide_context=True,  # Pass the Airflow context to the function
    dag = dag,
)

create_db_task = PythonOperator(
    task_id = 'create_db',
    python_callable = create_db_main,
    op_args=[user, password, host, port, new_db_name, db_url],
    provide_context=True,  # Pass the Airflow context to the function
    dag = dag,
)

create_tables_task = PythonOperator(
    task_id = 'create_tables',
    python_callable = create_tables_main,
    op_args=[db_url],
    provide_context=True,  # Pass the Airflow context to the function
    dag = dag,
)

load_data_task = PythonOperator(
    task_id = 'load_data',
    python_callable = load_data_main,
    op_args=[output_transformed, db_url, user, password],
    provide_context=True,  # Pass the Airflow context to the function
    dag = dag,
)

download_data_task >> import_clean_transform_task
import_clean_transform_task >> validate_data_task
validate_data_task >> create_db_task
create_db_task >> create_tables_task
create_tables_task >> load_data_task